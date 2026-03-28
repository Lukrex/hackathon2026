from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from .models import Request, Expert, Category
from .forms import RequestSubmissionForm, RequestFilterForm, RequestReviewForm, ExpertProfileForm
from .tasks import calculate_expert_matches


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


def api_docs(request):
    """API documentation page"""
    endpoints = [
        {
            'method': 'GET',
            'endpoint': '/api/requests/',
            'description': 'List all requests with filtering and sorting',
        },
        {
            'method': 'POST',
            'endpoint': '/api/requests/',
            'description': 'Create new request',
        },
        {
            'method': 'GET',
            'endpoint': '/api/experts/',
            'description': 'List all experts with search',
        },
        {
            'method': 'GET',
            'endpoint': '/api/matches/',
            'description': 'List expert matches',
        },
        {
            'method': 'GET',
            'endpoint': '/api/categories/',
            'description': 'List all request categories',
        },
    ]
    return render(request, 'api_docs.html', {'endpoints': endpoints})


@require_http_methods(["GET", "POST"])
def submit_request(request):
    """Public form for submitting new help requests"""
    if request.method == 'POST':
        form = RequestSubmissionForm(request.POST)
        if form.is_valid():
            try:
                new_request = form.save(commit=False)
                new_request.status = 'open'
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
    requests = Request.objects.all().order_by('due_date', '-created_at')

    # Filter out requests without due dates or put them at the end
    requests_with_due = requests.exclude(due_date__isnull=True)
    requests_without_due = requests.filter(due_date__isnull=True)
    requests = list(requests_with_due) + list(requests_without_due)

    dashboard_type = 'all'
    stats = {
        'total_requests': Request.objects.count(),
        'open_requests': Request.objects.filter(status__in=['open', 'in_review', 'waiting_expert']).count(),
        'in_progress': Request.objects.filter(status='in_progress').count(),
        'resolved': Request.objects.filter(status='resolved').count(),
        'total_experts': Expert.objects.count(),
    }

    return render(request, 'dashboard.html', {
        'requests': requests,
        'dashboard_type': dashboard_type,
        'stats': stats,
    })


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
            Q(expertise__icontains=search_term)
        )

    return render(request, 'expert_directory.html', {
        'experts': experts,
        'search_term': search_term or '',
        'availability_filter': availability_filter or '',
    })


@login_required
def request_detail(request, request_id):
    """Detailed view of a single request"""
    req = get_object_or_404(Request, id=request_id)
    suggested_matches = req.expert_matches.all().order_by('-match_score')[:10]

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
            # If coming from dashboard, redirect back
            if 'offer_help' in request.POST:
                return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error offering help: {str(e)}')

    return render(request, 'request_detail.html', {
        'request': req,
        'suggested_matches': suggested_matches,
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
