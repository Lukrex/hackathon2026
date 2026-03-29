from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import (
    Request,
    Expert,
    Category,
    RequestChatMessage,
    AdminChatMessage,
    CompanyChatMessage,
    DirectChatMessage,
    WorkerProfile,
)
from .forms import (
    RequestSubmissionForm,
    RequestFilterForm,
    RequestReviewForm,
    ExpertProfileForm,
    RegisterForm,
    UsernameEmailAuthenticationForm,
    RequestChatMessageForm,
    ChatMessageForm,
)
from .tasks import calculate_expert_matches


ACTIVE_REQUEST_STATUSES = ['open', 'in_review', 'waiting_expert', 'in_progress']


class RememberMeLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = UsernameEmailAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get('remember'):
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)
        return response


def is_tier1(user):
    """Tier 1: global super-admin — sees all requests, manages workers."""
    return bool(user and user.is_active and user.is_superuser)


def is_tier2(user):
    """Tier 2: company worker — sees only their assigned categories."""
    return bool(user and user.is_active and user.is_staff and not user.is_superuser)


def is_any_company(user):
    """Any company account (Tier 1 or Tier 2)."""
    return bool(user and user.is_active and (user.is_staff or user.is_superuser))


def is_admin_user(user):
    """Backward-compat alias for is_any_company."""
    return is_any_company(user)


def can_use_direct_company_chat(user_a, user_b):
    """Allow direct chat only between Tier 1 and Tier 2 accounts."""
    return (is_tier1(user_a) and is_tier2(user_b)) or (is_tier2(user_a) and is_tier1(user_b))


def is_request_chat_participant(user, req):
    """Requester and currently assigned experts can send request chat messages."""
    if req.submitted_by_id == user.id:
        return True

    try:
        expert = user.expert
    except Expert.DoesNotExist:
        return False

    return req.assigned_experts.filter(id=expert.id).exists()


def update_expert_busy_status(expert):
    """Set expert busy/free based on active assigned requests."""
    is_busy = expert.assigned_requests.filter(status__in=ACTIVE_REQUEST_STATUSES).exists()
    if expert.is_busy != is_busy:
        expert.is_busy = is_busy
        expert.save(update_fields=['is_busy'])


def compute_request_priority_score(req, today_date=None):
    """Compute request priority score (0-100) using deadline, age, and user karma."""
    if today_date is None:
        today_date = timezone.now().date()

    # Time factor: min(1 / D, 1), where D is days to deadline.
    if req.due_date:
        days_to_deadline = (req.due_date - today_date).days
        time_factor = 1.0 if days_to_deadline <= 0 else min(1.0 / days_to_deadline, 1.0)
    else:
        time_factor = 0.0

    # Age factor: V / (V + 10), where V is task age in days.
    task_age_days = max((today_date - req.created_at.date()).days, 0)
    age_factor = task_age_days / (task_age_days + 10) if task_age_days > 0 else 0.0

    # Karma factor: K / 36, capped to [0, 36].
    karma_points = 0
    if req.submitted_by_id:
        try:
            karma_points = req.submitted_by.expert.karma_points
        except Expert.DoesNotExist:
            karma_points = 0

    karma_factor = max(0.0, min(float(karma_points), 36.0)) / 36.0

    score = 100.0 * ((0.6 * time_factor) + (0.25 * age_factor) + (0.15 * karma_factor))
    return max(0.0, min(score, 100.0))


def compute_expert_recommendations(req, limit=6):
    """Compute live expert recommendations for a request based on relevance scoring."""
    # First try pre-computed AI matches
    ai_matches_qs = req.expert_matches.select_related('expert__user').prefetch_related(
        'expert__skills', 'expert__languages'
    ).order_by('-match_score')
    if ai_matches_qs.count() >= 3:
        # Return AI matches enriched with expert data
        return [{
            'expert': m.expert,
            'score': round(m.match_score),
            'reasoning': m.reasoning,
            'source': 'ai',
        } for m in ai_matches_qs[:limit]]

    # Fallback: compute live relevance scores
    request_skill_ids = set(req.target_skills.values_list('id', flat=True))
    request_lang_ids = set(req.required_languages.values_list('id', flat=True))
    req_words = set((req.title + ' ' + req.description).lower().split())

    availability_weight = {'high': 1.0, 'medium': 0.7, 'low': 0.3}

    experts = Expert.objects.select_related('user').prefetch_related('skills', 'languages').all()
    scored = []
    for expert in experts:
        score = 0.0

        # Skill overlap (40 pts)
        expert_skill_ids = set(expert.skills.values_list('id', flat=True))
        if request_skill_ids:
            overlap = len(request_skill_ids & expert_skill_ids)
            score += (overlap / len(request_skill_ids)) * 40
        elif expert_skill_ids:
            # No specific skills required — any expert with skills gets a small boost
            score += 10

        # Language overlap (20 pts)
        expert_lang_ids = set(expert.languages.values_list('id', flat=True))
        if request_lang_ids:
            lang_overlap = len(request_lang_ids & expert_lang_ids)
            score += (lang_overlap / len(request_lang_ids)) * 20

        # Keyword match in bio / work experience (20 pts)
        expert_text_words = set((expert.bio + ' ' + expert.work_experience).lower().split())
        kw_overlap = len(req_words & expert_text_words)
        score += min(kw_overlap * 2, 20)

        # Rating (10 pts)
        if expert.rating_count > 0:
            score += (expert.rating / 5.0) * 10

        # Availability (10 pts)
        score += availability_weight.get(expert.availability, 0.5) * 10

        if score > 0:
            skill_names = [s.name for s in expert.skills.all()]
            lang_names = [l.name for l in expert.languages.all()]
            reasons = []
            if request_skill_ids and expert_skill_ids & request_skill_ids:
                matched = [s.name for s in expert.skills.all() if s.id in request_skill_ids]
                reasons.append(f"Skills: {', '.join(matched)}")
            if request_lang_ids and expert_lang_ids & request_lang_ids:
                matched_langs = [l.name for l in expert.languages.all() if l.id in request_lang_ids]
                reasons.append(f"Languages: {', '.join(matched_langs)}")
            if expert.rating_count > 0:
                reasons.append(f"Rating: {expert.average_rating()}/5")
            scored.append({
                'expert': expert,
                'score': round(min(score, 100)),
                'reasoning': ' | '.join(reasons) if reasons else 'General match',
                'source': 'live',
            })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:limit]


def index(request):
    """Landing page / home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    stats = {
        'total_requests': Request.objects.count(),
        'total_experts': Expert.objects.count(),
        'resolved_requests': Request.objects.filter(status='resolved').count(),
        'categories_count': Category.objects.count(),
    }

    # Get recent requests
    recent_requests = Request.objects.all().order_by('-created_at')[:3]

    # Get featured experts (most helpful)
    featured_experts = Expert.objects.all().order_by('-help_provided')[:3]

    return render(request, 'index.html', {
        'stats': stats,
        'recent_requests': recent_requests,
        'featured_experts': featured_experts,
    })


def about(request):
    """About page"""
    return render(request, 'about.html')


def features(request):
    """Features page"""
    features_list = [
        {
            'icon': '📝',
            'title': 'Jednoduché zadávanie žiadostí',
            'description': 'Komunita jednoducho zadáva svoje potreby cez verejný formulár.',
        },
        {
            'icon': '🔍',
            'title': 'Manuálne preverovanie',
            'description': 'Admin tím skúma žiadosti a zaraďuje ich do kategórií.',
        },
        {
            'icon': '🧠',
            'title': 'Inteligentný matching',
            'description': 'Systém navrhuje najvhodnejších expertov na základe skúsenosti.',
        },
        {
            'icon': '📧',
            'title': 'Email notifikácie',
            'description': 'Všetci účastníci dostávajú profesionálne email potvrdenia.',
        },
        {
            'icon': '📊',
            'title': 'Tracking a štatistiky',
            'description': 'Sledujte vplyv a merateľné výsledky pomoci.',
        },
        {
            'icon': '🔗',
            'title': 'Notion integrácia',
            'description': 'Export údajov a synchronizácia s vašim Notion workspace.',
        },
    ]
    return render(request, 'features.html', {'features': features_list})


def how_it_works(request):
    """How it works page"""
    steps = [
        {
            'number': '1',
            'title': 'Zadaj odkázal',
            'description': 'Comunita zadá svoju potrebu cez jednoduchý formulár.',
            'icon': '📝',
        },
        {
            'number': '2',
            'title': 'Preverenie',
            'description': 'Náš tím preskúma žiadosť a zaradí ju do správnej kategórie.',
            'icon': '🔍',
        },
        {
            'number': '3',
            'title': 'Matching',
            'description': 'Systém nájde najlepšie vyhovujúcich expertov z komunity.',
            'icon': '🧠',
        },
        {
            'number': '4',
            'title': 'Spojenie',
            'description': 'Experti sa dozvedia o požiadavke a kontaktujú žiadateľa.',
            'icon': '🤝',
        },
        {
            'number': '5',
            'title': 'Pomoc',
            'description': 'Experti poskytnú know-how a pomoc vyriešiť problém.',
            'icon': '💡',
        },
        {
            'number': '6',
            'title': 'Tracking',
            'description': 'Merame vplyv a zaznamenávame úspešné riešenia.',
            'icon': '📊',
        },
    ]
    return render(request, 'how_it_works.html', {'steps': steps})


def _group_skills_by_theme(queryset):
    theme_rules = [
        ('Technology', ['python', 'javascript', 'react', 'django', 'node', 'api', 'data', 'ai', 'ml', 'cloud', 'devops', 'mobile', 'frontend', 'backend']),
        ('Business & Management', ['strategy', 'product', 'project', 'operations', 'management', 'business', 'finance', 'sales']),
        ('Marketing & Growth', ['marketing', 'seo', 'brand', 'content', 'social', 'growth', 'ads', 'campaign']),
        ('Design & UX', ['design', 'ui', 'ux', 'figma', 'visual', 'research']),
        ('People & Communication', ['hr', 'recruit', 'talent', 'coaching', 'communication', 'public speaking']),
    ]

    grouped = {theme: [] for theme, _ in theme_rules}
    grouped['Other'] = []

    for skill in queryset:
        normalized = skill.name.lower()
        matched = False
        for theme, keywords in theme_rules:
            if any(word in normalized for word in keywords):
                grouped[theme].append(skill)
                matched = True
                break
        if not matched:
            grouped['Other'].append(skill)

    themed = []
    for theme, _ in theme_rules:
        if grouped[theme]:
            themed.append((theme, grouped[theme]))
    if grouped['Other']:
        themed.append(('Other', grouped['Other']))
    return themed


@login_required
@require_http_methods(["GET", "POST"])
def submit_request(request):
    """Authenticated form for submitting new help requests"""
    if request.method == 'POST':
        form = RequestSubmissionForm(request.POST)
        if form.is_valid():
            try:
                new_request = form.save(commit=False)
                new_request.status = 'open'
                new_request.submitted_by = request.user
                new_request.requester_email = request.user.email or f'{request.user.username}@local.invalid'
                new_request.save()
                form.save_m2m()

                # Trigger expert matching asynchronously
                # calculate_expert_matches.delay(new_request.id)

                messages.success(
                    request,
                    f'✅ Your request "{new_request.title}" has been submitted successfully! '
                    f'A confirmation email has been sent to {new_request.requester_email}'
                )
                return redirect('request_submitted', request_id=new_request.id)
            except Exception as e:
                messages.error(request, f'Error saving request: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = RequestSubmissionForm(initial={'requester_type': 'community_member'})

    skills_qs = form.fields['target_skills'].queryset
    languages_qs = form.fields['required_languages'].queryset
    skill_groups = _group_skills_by_theme(skills_qs)
    wanted_languages = list(languages_qs)
    selected_target_skills = set(request.POST.getlist('target_skills')) if request.method == 'POST' else set()
    selected_required_languages = set(request.POST.getlist('required_languages')) if request.method == 'POST' else set()

    return render(request, 'submit_request.html', {
        'form': form,
        'skill_groups': skill_groups,
        'wanted_languages': wanted_languages,
        'selected_target_skills': selected_target_skills,
        'selected_required_languages': selected_required_languages,
    })


def request_submitted(request, request_id):
    """Confirmation page after request submission"""
    req = get_object_or_404(Request, id=request_id)
    return render(request, 'request_submitted.html', {
        'request': req,
        'next_steps': [
            'Our team reviews the request',
            'We select matching experts from the community',
            'We connect you with relevant help offers'
        ]
    })


@login_required
def dashboard(request):
    """Role-based dashboard: admins manage assignments, users track requests/tasks."""
    if is_tier1(request.user):
        # ── Tier 1: global admin — sees all requests ──────────────────────
        unassigned_requests_qs = Request.objects.filter(
            status__in=ACTIVE_REQUEST_STATUSES,
            assigned_experts__isnull=True,
        ).select_related('category', 'submitted_by').prefetch_related('offered_experts__user').distinct().order_by('-created_at')

        assigned_requests_qs = Request.objects.filter(
            status__in=ACTIVE_REQUEST_STATUSES,
            assigned_experts__isnull=False,
        ).prefetch_related('assigned_experts__user', 'offered_experts__user').select_related('category').distinct().order_by('-created_at')

        free_experts = Expert.objects.select_related('user').exclude(
            assigned_requests__status__in=ACTIVE_REQUEST_STATUSES
        ).order_by('-karma_points', '-help_provided').distinct()

        stats = {
            'unassigned_requests_count': unassigned_requests_qs.count(),
            'assigned_requests_count': assigned_requests_qs.count(),
            'free_experts_count': free_experts.count(),
            'busy_experts_count': Expert.objects.filter(assigned_requests__status__in=ACTIVE_REQUEST_STATUSES).distinct().count(),
        }

        return render(request, 'admin_dashboard.html', {
            'stats': stats,
            'unassigned_requests': unassigned_requests_qs,
            'assigned_requests': assigned_requests_qs,
            'free_experts': free_experts,
            'is_tier1': True,
        })

    if is_tier2(request.user):
        # ── Tier 2: worker — sees only their assigned categories ───────────
        try:
            allowed_category_ids = list(request.user.worker_profile.categories.values_list('id', flat=True))
            my_category_names = list(request.user.worker_profile.categories.values_list('name', flat=True))
        except WorkerProfile.DoesNotExist:
            allowed_category_ids = []
            my_category_names = []

        unassigned_requests_qs = Request.objects.filter(
            status__in=ACTIVE_REQUEST_STATUSES,
            assigned_experts__isnull=True,
            category_id__in=allowed_category_ids,
        ).select_related('category', 'submitted_by').prefetch_related('offered_experts__user').distinct().order_by('-created_at')

        assigned_requests_qs = Request.objects.filter(
            status__in=ACTIVE_REQUEST_STATUSES,
            assigned_experts__isnull=False,
            category_id__in=allowed_category_ids,
        ).prefetch_related('assigned_experts__user', 'offered_experts__user').select_related('category').distinct().order_by('-created_at')

        free_experts = Expert.objects.select_related('user').exclude(
            assigned_requests__status__in=ACTIVE_REQUEST_STATUSES
        ).order_by('-karma_points', '-help_provided').distinct()

        stats = {
            'unassigned_requests_count': unassigned_requests_qs.count(),
            'assigned_requests_count': assigned_requests_qs.count(),
            'free_experts_count': free_experts.count(),
            'busy_experts_count': Expert.objects.filter(assigned_requests__status__in=ACTIVE_REQUEST_STATUSES).distinct().count(),
        }

        return render(request, 'admin_dashboard.html', {
            'stats': stats,
            'unassigned_requests': unassigned_requests_qs,
            'assigned_requests': assigned_requests_qs,
            'free_experts': free_experts,
            'is_tier1': False,
            'my_category_names': my_category_names,
        })

    all_requests = list(Request.objects.select_related('submitted_by').all())

    today_date = timezone.now().date()
    for req in all_requests:
        req.algorithm_priority_score = compute_request_priority_score(req, today_date=today_date)

    requests = sorted(
        all_requests,
        key=lambda req: (req.algorithm_priority_score, req.created_at.timestamp()),
        reverse=True,
    )

    my_requests_qs = Request.objects.filter(submitted_by=request.user).prefetch_related('assigned_experts').order_by('-created_at')
    my_requests = list(my_requests_qs)
    my_pending_count = my_requests_qs.filter(is_resolved_by_creator=False).count()
    my_done_count = my_requests_qs.filter(is_resolved_by_creator=True).count()

    expert_assigned_tasks = []
    try:
        expert_profile = request.user.expert
        expert_assigned_tasks = list(
            expert_profile.assigned_requests.filter(status__in=ACTIVE_REQUEST_STATUSES)
            .select_related('category', 'submitted_by')
            .order_by('-created_at')
        )
    except Expert.DoesNotExist:
        expert_profile = None

    stats = {
        'total_requests': Request.objects.count(),
        'open_requests': Request.objects.filter(status__in=['open', 'in_review', 'waiting_expert']).count(),
        'in_progress': Request.objects.filter(status='in_progress').count(),
        'resolved': Request.objects.filter(status='resolved').count(),
        'total_experts': Expert.objects.count(),
        'my_requests_count': my_requests_qs.count(),
        'my_pending_count': my_pending_count,
        'my_done_count': my_done_count,
        'my_assigned_tasks_count': len(expert_assigned_tasks),
    }

    return render(request, 'dashboard.html', {
        'requests': requests,
        'my_requests': my_requests,
        'expert_assigned_tasks': expert_assigned_tasks,
        'expert_profile': expert_profile,
        'stats': stats,
    })


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def admin_assign_expert(request, request_id):
    """Admin assigns a free expert to a request."""
    req = get_object_or_404(Request.objects.prefetch_related('assigned_experts'), id=request_id)

    if req.status in ['resolved', 'rejected']:
        messages.error(request, 'Cannot assign expert to completed/rejected request.')
        return redirect('request_detail', request_id=request_id)

    expert_id = request.POST.get('expert_id')
    if not expert_id:
        messages.error(request, 'Please choose an expert to assign.')
        return redirect('request_detail', request_id=request_id)

    try:
        expert_id = int(expert_id)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid expert selection.')
        return redirect('request_detail', request_id=request_id)

    expert = Expert.objects.select_related('user').filter(id=expert_id).first()
    if not expert:
        messages.error(request, 'Expert does not exist.')
        return redirect('request_detail', request_id=request_id)

    # Real check: already on this task?
    if req.assigned_experts.filter(id=expert.id).exists():
        messages.info(request, f'{expert} is already assigned to this task.')
        return redirect('request_detail', request_id=request_id)

    # Real check: busy on a different active task?
    is_actually_busy = expert.assigned_requests.filter(
        status__in=ACTIVE_REQUEST_STATUSES
    ).exclude(id=req.id).exists()
    if is_actually_busy:
        messages.error(request, f'{expert} is currently busy on another task.')
        return redirect('request_detail', request_id=request_id)

    with transaction.atomic():
        req.assigned_experts.add(expert)  # add without clearing — supports multiple experts per task
        if req.status in ['open', 'in_review']:
            req.status = 'waiting_expert'
            req.save(update_fields=['status', 'updated_at'])

        expert.is_busy = True
        expert.save(update_fields=['is_busy'])

    messages.success(request, f'Assigned {expert} to "{req.title}".')
    return redirect('request_detail', request_id=request_id)


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def admin_unassign_expert(request, request_id):
    """Admin removes an expert from a corporate request."""
    req = get_object_or_404(Request.objects.prefetch_related('assigned_experts'), id=request_id)

    expert_id = request.POST.get('expert_id')
    if not expert_id:
        messages.error(request, 'No expert specified.')
        return redirect('request_detail', request_id=request_id)

    try:
        expert_id = int(expert_id)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid expert selection.')
        return redirect('request_detail', request_id=request_id)

    expert = Expert.objects.filter(id=expert_id).first()
    if not expert:
        messages.error(request, 'Expert does not exist.')
        return redirect('request_detail', request_id=request_id)

    if not req.assigned_experts.filter(id=expert.id).exists():
        messages.error(request, 'That expert is not assigned to this request.')
        return redirect('request_detail', request_id=request_id)

    with transaction.atomic():
        req.assigned_experts.remove(expert)
        if req.status in ['waiting_expert', 'in_progress'] and not req.assigned_experts.exists():
            req.status = 'open'
            req.save(update_fields=['status', 'updated_at'])
        update_expert_busy_status(expert)

    messages.success(request, f'Unassigned {expert} from "{req.title}".')
    return redirect('request_detail', request_id=request_id)


@login_required
@user_passes_test(is_tier1)
@require_http_methods(["POST"])
def admin_delete_request(request, request_id):
    """Tier 1 admin permanently deletes a request."""
    req = get_object_or_404(Request.objects.prefetch_related('assigned_experts'), id=request_id)
    request_title = req.title
    assigned_experts = list(req.assigned_experts.all())

    with transaction.atomic():
        req.delete()
        for expert in assigned_experts:
            update_expert_busy_status(expert)

    messages.success(request, f'Request "{request_title}" has been deleted.')
    return redirect('dashboard')


@login_required
@require_http_methods(["POST"])
def leave_assigned_request(request, request_id):
    """Assigned expert can leave an active request, becoming free if no other active tasks."""
    req = get_object_or_404(Request.objects.prefetch_related('assigned_experts'), id=request_id)

    try:
        expert = request.user.expert
    except Expert.DoesNotExist:
        messages.error(request, 'Only experts can leave assigned tasks.')
        return HttpResponseRedirect('/dashboard/')

    if not req.assigned_experts.filter(id=expert.id).exists():
        messages.error(request, 'You are not assigned to this task.')
        return HttpResponseRedirect('/dashboard/')

    with transaction.atomic():
        req.assigned_experts.remove(expert)
        if req.status in ['waiting_expert', 'in_progress'] and not req.assigned_experts.exists():
            req.status = 'open'
            req.save(update_fields=['status', 'updated_at'])

        update_expert_busy_status(expert)

    messages.info(request, f'You left task "{req.title}".')
    return HttpResponseRedirect('/dashboard/')


@login_required
@require_http_methods(["POST"])
def mark_request_done(request, request_id):
    """Allow a request creator to mark their own request as done/resolved."""
    req = get_object_or_404(Request.objects.prefetch_related('assigned_experts'), id=request_id)

    if req.submitted_by_id != request.user.id:
        messages.error(request, 'You can only mark your own requests as done.')
        return redirect('dashboard')

    if req.is_resolved_by_creator:
        messages.info(request, f'Request "{req.title}" is already marked as done.')
        return HttpResponseRedirect('/dashboard/#my-requests')

    selected_expert = req.completed_by_expert or req.assigned_experts.first()
    if not selected_expert:
        messages.error(request, 'No assigned expert found. Ask admin to assign an expert first.')
        return HttpResponseRedirect('/dashboard/#my-requests')

    now = timezone.now()
    with transaction.atomic():
        req.is_resolved_by_creator = True
        req.creator_resolved_at = now
        req.completed_by_expert = selected_expert

        if req.status != 'resolved':
            req.status = 'resolved'
            if not req.resolved_at:
                req.resolved_at = now

        req.save(update_fields=[
            'is_resolved_by_creator',
            'creator_resolved_at',
            'completed_by_expert',
            'status',
            'resolved_at',
            'updated_at',
        ])

        selected_expert.karma_points += 1
        selected_expert.help_provided += 1
        selected_expert.save(update_fields=['karma_points', 'help_provided'])
        update_expert_busy_status(selected_expert)

    messages.success(
        request,
        f'Request "{req.title}" has been marked as done. {selected_expert} received +1 karma point.'
    )
    return HttpResponseRedirect('/dashboard/#my-requests')


@login_required
@require_http_methods(["GET", "POST"])
def review_request(request, request_id):
    """Admin view for reviewing and categorizing requests"""
    req = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        form = RequestReviewForm(request.POST, instance=req)
        if form.is_valid():
            reviewed_req = form.save(commit=False)
            reviewed_req.reviewed_by = request.user
            reviewed_req.save()

            messages.success(request, f'✅ Žiadosť "{req.title}" bola overená')

            # Trigger expert matching if not already done
            if reviewed_req.status == 'in_review':
                calculate_expert_matches.delay(reviewed_req.id)

            return redirect('dashboard')
    else:
        form = RequestReviewForm(instance=req)

    # Get suggested experts
    suggested_experts = req.expert_matches.all().order_by('-match_score')[:5]

    return render(request, 'review_request.html', {
        'request': req,
        'form': form,
        'suggested_experts': suggested_experts,
    })


@login_required
def expert_directory(request):
    """Browse expert profiles"""
    experts = Expert.objects.all().order_by('-help_provided')

    availability_filter = request.GET.get('availability')
    if availability_filter:
        experts = experts.filter(availability=availability_filter)

    search_term = request.GET.get('search')
    if search_term:
        experts = experts.filter(
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term) |
            Q(skills__name__icontains=search_term) |
            Q(languages__name__icontains=search_term) |
            Q(work_experience__icontains=search_term)
        )

    return render(request, 'expert_directory.html', {
        'experts': experts,
        'search_term': search_term or '',
        'availability_filter': availability_filter or '',
    })


@login_required
def user_profile(request, expert_id):
    """Public profile page for an expert"""
    expert = get_object_or_404(Expert.objects.select_related('user'), id=expert_id)
    open_requests_helped_qs = expert.assigned_requests.select_related('submitted_by').filter(
        status__in=['open', 'in_review', 'waiting_expert', 'in_progress']
    )

    today_date = timezone.now().date()
    open_requests_helped = sorted(
        list(open_requests_helped_qs),
        key=lambda req: (compute_request_priority_score(req, today_date=today_date), req.created_at.timestamp()),
        reverse=True,
    )[:10]

    return render(request, 'expert_profile.html', {
        'expert': expert,
        'open_requests_helped': open_requests_helped,
    })


@login_required
def request_detail(request, request_id):
    """Detailed view of a single request"""
    req = get_object_or_404(Request, id=request_id)
    admin_view = request.user.is_authenticated and is_admin_user(request.user)

    # Check if current user is an expert and can offer help
    can_offer_help = False
    has_offered_help = False
    is_assigned_here = False
    if not admin_view:
        try:
            expert = request.user.expert
            can_offer_help = req.status in ACTIVE_REQUEST_STATUSES
            has_offered_help = req.offered_experts.filter(id=expert.id).exists()
            is_assigned_here = req.assigned_experts.filter(id=expert.id).exists()
        except Expert.DoesNotExist:
            pass

    if request.method == 'POST' and 'offer_help' in request.POST:
        try:
            expert = request.user.expert
        except Expert.DoesNotExist:
            messages.error(request, 'Only experts can offer help.')
            return redirect('request_detail', request_id=request_id)

        if req.status not in ACTIVE_REQUEST_STATUSES:
            messages.info(request, 'This request is no longer accepting offers.')
            return redirect('request_detail', request_id=request_id)

        if req.assigned_experts.filter(id=expert.id).exists():
            messages.info(request, 'You are already assigned to this request.')
            return redirect('request_detail', request_id=request_id)

        if req.offered_experts.filter(id=expert.id).exists():
            messages.info(request, 'Your offer is already visible to admins.')
            return redirect('request_detail', request_id=request_id)

        req.offered_experts.add(expert)
        messages.success(request, 'Your offer to help is now visible to admins.')

        if request.POST.get('offer_help_source') == 'dashboard':
            return redirect('dashboard')
        return redirect('request_detail', request_id=request_id)

    # Compute expert recommendations (AI matches or live scoring)
    recommended_experts = compute_expert_recommendations(req, limit=6)

    # Fresh real-time busy/assigned state for each recommended expert
    already_assigned_ids = set(req.assigned_experts.values_list('id', flat=True))
    busy_elsewhere_ids = set(
        Expert.objects.filter(
            assigned_requests__status__in=ACTIVE_REQUEST_STATUSES
        ).exclude(
            assigned_requests=req
        ).values_list('id', flat=True)
    )
    for rec in recommended_experts:
        rec['is_assigned_here'] = rec['expert'].id in already_assigned_ids
        rec['is_busy'] = rec['expert'].id in busy_elsewhere_ids

    return render(request, 'request_detail.html', {
        'request': req,
        'recommended_experts': recommended_experts,
        'can_offer_help': can_offer_help,
        'has_offered_help': has_offered_help,
        'is_assigned_here': is_assigned_here,
        'is_admin': admin_view,
        'is_tier1': is_tier1(request.user),
        'can_access_request_chat': admin_view or is_request_chat_participant(request.user, req),
    })


@login_required
@require_http_methods(["GET", "POST"])
def request_chat(request, request_id):
    """Conversation for one request between requester and assigned experts."""
    req = get_object_or_404(
        Request.objects.select_related('submitted_by').prefetch_related('assigned_experts__user'),
        id=request_id
    )

    is_admin = is_admin_user(request.user)
    can_send = is_request_chat_participant(request.user, req)
    if not (is_admin or can_send):
        messages.error(request, 'You do not have access to this request chat.')
        return redirect('dashboard')

    if request.method == 'POST':
        if not can_send:
            messages.error(request, 'Only requester and assigned experts can send messages in this chat.')
            return redirect('request_chat', request_id=req.id)

        form = RequestChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.request = req
            chat_message.sender = request.user
            chat_message.save()
            return redirect('request_chat', request_id=req.id)
    else:
        form = RequestChatMessageForm()

    chat_messages = req.chat_messages.select_related('sender').order_by('created_at')

    return render(request, 'request_chat.html', {
        'request_obj': req,
        'chat_messages': chat_messages,
        'form': form,
        'can_send': can_send,
        'is_admin': is_admin,
    })


@login_required
@user_passes_test(is_tier1)
def admin_manage_workers(request):
    """Tier 1: manage Tier 2 role and category assignments."""
    from django.contrib.auth.models import User as DjangoUser
    search_query = (request.GET.get('q') or '').strip()

    users_qs = DjangoUser.objects.filter(is_superuser=False)
    if search_query:
        users_qs = users_qs.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    users_qs = users_qs.order_by('-is_staff', 'username')
    all_categories = Category.objects.all()

    workers = []
    for worker in users_qs:
        profile, _ = WorkerProfile.objects.get_or_create(user=worker)
        workers.append({
            'user': worker,
            'profile': profile,
            'is_tier2': bool(worker.is_staff),
            'selected_category_ids': set(profile.categories.values_list('id', flat=True)),
        })

    return render(request, 'manage_workers.html', {
        'workers': workers,
        'all_categories': all_categories,
        'search_query': search_query,
    })


@login_required
@user_passes_test(is_tier1)
@require_http_methods(["POST"])
def admin_set_worker_role(request, worker_id):
    """Tier 1: toggle a user in/out of Tier 2 worker role."""
    from django.contrib.auth.models import User as DjangoUser
    worker = get_object_or_404(DjangoUser, id=worker_id, is_superuser=False)

    make_tier2 = request.POST.get('make_tier2') == '1'
    worker.is_staff = make_tier2
    worker.save(update_fields=['is_staff'])

    profile, _ = WorkerProfile.objects.get_or_create(user=worker)
    if not make_tier2:
        profile.categories.clear()
        messages.success(request, f'{worker.username} removed from Tier 2 worker accounts.')
    else:
        messages.success(request, f'{worker.username} is now a Tier 2 worker. You can assign categories below.')

    return redirect('admin_manage_workers')


@login_required
@user_passes_test(is_tier1)
@require_http_methods(["POST"])
def admin_set_worker_categories(request, worker_id):
    """Tier 1: update category assignments for a Tier 2 worker."""
    from django.contrib.auth.models import User as DjangoUser
    worker = get_object_or_404(DjangoUser, id=worker_id, is_staff=True, is_superuser=False)
    profile, _ = WorkerProfile.objects.get_or_create(user=worker)
    category_ids = request.POST.getlist('categories')
    profile.categories.set(Category.objects.filter(id__in=category_ids))
    messages.success(request, f'Categories updated for {worker.username}.')
    return redirect('admin_manage_workers')


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["GET", "POST"])
def chats(request):
    """Unified chat hub for company accounts with role-based tabs."""
    if is_tier1(request.user):
        allowed_tabs = {'company', 'admin', 'direct'}
        default_tab = 'company'
        partner_label = 'Tier 2 worker'
        partner_users = User.objects.filter(is_staff=True, is_superuser=False).order_by('username')
    else:
        allowed_tabs = {'company', 'direct'}
        default_tab = 'company'
        partner_label = 'Tier 1 admin'
        partner_users = User.objects.filter(is_superuser=True).order_by('username')

    active_tab = request.GET.get('tab', default_tab)
    if active_tab not in allowed_tabs:
        active_tab = default_tab

    selected_partner_id = request.GET.get('partner')
    selected_partner = None
    if selected_partner_id:
        selected_partner = partner_users.filter(id=selected_partner_id).first()
    if not selected_partner and partner_users.exists():
        selected_partner = partner_users.first()

    if request.method == 'POST':
        action = request.POST.get('action')
        message_form = ChatMessageForm(request.POST)
        if message_form.is_valid():
            text = message_form.cleaned_data['message']
            if action == 'company':
                CompanyChatMessage.objects.create(sender=request.user, message=text)
                return HttpResponseRedirect(f"{reverse('chats')}?tab=company")

            if action == 'admin':
                if not is_tier1(request.user):
                    messages.error(request, 'Only Tier 1 accounts can post in Admin Chat.')
                else:
                    AdminChatMessage.objects.create(sender=request.user, message=text)
                    return HttpResponseRedirect(f"{reverse('chats')}?tab=admin")

            if action == 'direct':
                partner_id = request.POST.get('partner_id')
                partner = partner_users.filter(id=partner_id).first()
                if not partner:
                    messages.error(request, f'Select a valid {partner_label.lower()} first.')
                elif not can_use_direct_company_chat(request.user, partner):
                    messages.error(request, 'Direct chat is allowed only between Tier 1 and Tier 2 accounts.')
                else:
                    DirectChatMessage.objects.create(
                        sender=request.user,
                        recipient=partner,
                        message=text,
                    )
                    return HttpResponseRedirect(f"{reverse('chats')}?tab=direct&partner={partner.id}")
        else:
            messages.error(request, 'Message cannot be empty.')

    company_chat_messages = CompanyChatMessage.objects.select_related('sender').order_by('created_at')
    admin_chat_messages = AdminChatMessage.objects.select_related('sender').order_by('created_at') if is_tier1(request.user) else []

    direct_chat_messages = []
    if selected_partner and can_use_direct_company_chat(request.user, selected_partner):
        direct_chat_messages = DirectChatMessage.objects.filter(
            Q(sender=request.user, recipient=selected_partner)
            | Q(sender=selected_partner, recipient=request.user)
        ).select_related('sender', 'recipient').order_by('created_at')

    return render(request, 'chats.html', {
        'is_tier1': is_tier1(request.user),
        'is_tier2': is_tier2(request.user),
        'active_tab': active_tab,
        'company_chat_messages': company_chat_messages,
        'admin_chat_messages': admin_chat_messages,
        'partner_users': partner_users,
        'selected_partner': selected_partner,
        'direct_chat_messages': direct_chat_messages,
    })


@login_required
@user_passes_test(is_admin_user)
def admin_chat(request):
    """Legacy route: redirect to unified chats hub."""
    return redirect('chats')


from django.contrib.auth import login


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Víta vás {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form,
    })


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, 'Company accounts cannot edit expert profiles.')
        return redirect('dashboard')

    try:
        expert = request.user.expert
    except Expert.DoesNotExist:
        # Create expert profile if it doesn't exist
        expert = Expert.objects.create(user=request.user)

    if request.method == 'POST':
        form = ExpertProfileForm(request.POST, instance=expert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
    else:
        form = ExpertProfileForm(instance=expert)

    skill_groups = _group_skills_by_theme(form.fields['skills'].queryset)
    known_languages = list(form.fields['languages'].queryset)
    selected_skills = set(request.POST.getlist('skills')) if request.method == 'POST' else set(
        str(skill_id) for skill_id in expert.skills.values_list('id', flat=True)
    )
    selected_languages = set(request.POST.getlist('languages')) if request.method == 'POST' else set(
        str(language_id) for language_id in expert.languages.values_list('id', flat=True)
    )

    return render(request, 'edit_profile.html', {
        'form': form,
        'expert': expert,
        'skill_groups': skill_groups,
        'known_languages': known_languages,
        'selected_skills': selected_skills,
        'selected_languages': selected_languages,
    })
