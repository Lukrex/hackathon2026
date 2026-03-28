from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from .models import Request, Expert, Category
from .forms import RequestSubmissionForm, RequestFilterForm, RequestReviewForm
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
                new_request.priority = 'medium'
                new_request.save()

                # Trigger expert matching asynchronously
                # calculate_expert_matches.delay(new_request.id)  # Commented out for testing

                messages.success(
                    request,
                    f'✅ Tvoja žiadosť "{new_request.title}" bola prijatá! '
                    f'Potvrdenie bolo zaslané na {new_request.requester_email}'
                )
                return redirect('request_submitted', request_id=new_request.id)
            except Exception as e:
                messages.error(request, f'Chyba pri ukladaní žiadosti: {str(e)}')
        else:
            messages.error(request, 'Prosím, opravte chyby vo formulári.')
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
            'Náš tím preskúma tvoju žiadosť',
            'Vyhľadáme vhodných expertov z komunity',
            'Skontaktujeme ťa s ponukami pomoci'
        ]
    })


@login_required
def dashboard(request):
    """User dashboard showing requests relevant to them"""
    try:
        expert = request.user.expert
        # User is an expert, show assigned requests
        requests = expert.assigned_requests.all().order_by('-created_at')
        dashboard_type = 'expert'
        stats = {
            'assigned_requests': requests.count(),
            'open_requests': requests.filter(status__in=['open', 'in_review', 'waiting_expert']).count(),
            'in_progress': requests.filter(status='in_progress').count(),
            'resolved': requests.filter(status='resolved').count(),
        }
    except Expert.DoesNotExist:
        # User is not an expert, show general stats or their submitted requests
        # For now, show all open requests they could help with
        requests = Request.objects.filter(status__in=['open', 'in_review']).order_by('-created_at')[:10]
        dashboard_type = 'user'
        stats = {
            'available_requests': requests.count(),
            'total_requests': Request.objects.count(),
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

    return render(request, 'request_detail.html', {
        'request': req,
        'suggested_matches': suggested_matches,
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
