from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import Request, Expert, Category
from .forms import RequestSubmissionForm, RequestFilterForm, RequestReviewForm, ExpertProfileForm
from .tasks import calculate_expert_matches


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


@require_http_methods(["GET", "POST"])
def submit_request(request):
    """Public form for submitting new help requests"""
    if request.method == 'POST':
        form = RequestSubmissionForm(request.POST)
        if form.is_valid():
            try:
                new_request = form.save(commit=False)
                new_request.status = 'open'
                if request.user.is_authenticated:
                    new_request.submitted_by = request.user
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

    categories = Category.objects.all()
    return render(request, 'submit_request.html', {
        'form': form,
        'categories': categories,
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
    """User dashboard showing all requests sorted by due date"""
    # Show all requests sorted by due date (closest first), then by created date
    all_qs = Request.objects.all().order_by('due_date', '-created_at')
    requests_with_due = all_qs.exclude(due_date__isnull=True)
    requests_without_due = all_qs.filter(due_date__isnull=True)
    requests = list(requests_with_due) + list(requests_without_due)

    # My requests: submitted by this user (via the submitted_by FK)
    my_requests_qs = Request.objects.filter(submitted_by=request.user).prefetch_related('assigned_experts').order_by('-created_at')
    my_requests = list(my_requests_qs)
    my_pending_count = my_requests_qs.filter(is_resolved_by_creator=False).count()
    my_done_count = my_requests_qs.filter(is_resolved_by_creator=True).count()

    dashboard_type = 'all'
    stats = {
        'total_requests': Request.objects.count(),
        'open_requests': Request.objects.filter(status__in=['open', 'in_review', 'waiting_expert']).count(),
        'in_progress': Request.objects.filter(status='in_progress').count(),
        'resolved': Request.objects.filter(status='resolved').count(),
        'total_experts': Expert.objects.count(),
        'my_requests_count': my_requests_qs.count(),
        'my_pending_count': my_pending_count,
        'my_done_count': my_done_count,
    }

    return render(request, 'dashboard.html', {
        'requests': requests,
        'my_requests': my_requests,
        'dashboard_type': dashboard_type,
        'stats': stats,
    })


@login_required
@require_http_methods(["POST"])
def mark_request_done(request, request_id):
    """Allow a request creator to mark their own request as done/resolved."""
    req = get_object_or_404(Request, id=request_id)

    if req.submitted_by_id != request.user.id:
        messages.error(request, 'You can only mark your own requests as done.')
        return redirect('dashboard')

    if req.is_resolved_by_creator:
        messages.info(request, f'Request "{req.title}" is already marked as done.')
        return HttpResponseRedirect('/dashboard/#my-requests')

    selected_expert_id = request.POST.get('completed_expert_id')
    if not selected_expert_id:
        messages.error(request, 'Please select the expert who completed this request.')
        return HttpResponseRedirect('/dashboard/#my-requests')

    try:
        selected_expert_id = int(selected_expert_id)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid expert selection.')
        return HttpResponseRedirect('/dashboard/#my-requests')

    selected_expert = req.assigned_experts.filter(id=selected_expert_id).first()
    if not selected_expert:
        messages.error(request, 'Selected expert must be assigned to this request.')
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
    open_requests_helped = expert.assigned_requests.filter(
        status__in=['open', 'in_review', 'waiting_expert', 'in_progress']
    ).order_by('due_date', '-created_at')[:10]

    return render(request, 'expert_profile.html', {
        'expert': expert,
        'open_requests_helped': open_requests_helped,
    })


@login_required
def request_detail(request, request_id):
    """Detailed view of a single request"""
    req = get_object_or_404(Request, id=request_id)

    # Check if current user is an expert and can offer help
    can_offer_help = False
    has_offered_help = False
    try:
        expert = request.user.expert
        can_offer_help = True
        has_offered_help = req.assigned_experts.filter(id=expert.id).exists()
    except Expert.DoesNotExist:
        pass

    if request.method == 'POST' and can_offer_help and not has_offered_help:
        # Expert is offering help
        try:
            expert = request.user.expert
            req.assigned_experts.add(expert)
            messages.success(request, f'You have successfully offered help for "{req.title}"!')
            has_offered_help = True
            if 'offer_help' in request.POST:
                return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error offering help: {str(e)}')

    # Compute expert recommendations (AI matches or live scoring)
    recommended_experts = compute_expert_recommendations(req, limit=6)

    return render(request, 'request_detail.html', {
        'request': req,
        'recommended_experts': recommended_experts,
        'can_offer_help': can_offer_help,
        'has_offered_help': has_offered_help,
    })


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Víta vás {user.username}!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form,
    })


@login_required
def edit_profile(request):
    """Edit user profile"""
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

    return render(request, 'edit_profile.html', {
        'form': form,
        'expert': expert,
    })
