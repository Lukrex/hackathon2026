from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from .models import Request, Expert, Category
from .forms import RequestSubmissionForm, RequestFilterForm, RequestReviewForm
from .tasks import calculate_expert_matches


@require_http_methods(["GET", "POST"])
def submit_request(request):
    """Public form for submitting new help requests"""
    if request.method == 'POST':
        form = RequestSubmissionForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.status = 'open'
            new_request.priority = 'medium'
            new_request.save()

            # Trigger expert matching asynchronously
            calculate_expert_matches.delay(new_request.id)

            messages.success(
                request,
                f'✅ Tvoja žiadosť "{new_request.title}" bola prijatá! '
                f'Potvrdenie bolo zaslané na {new_request.requester_email}'
            )
            return redirect('request_submitted', request_id=new_request.id)
    else:
        form = RequestSubmissionForm()

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
    """Admin dashboard for request management"""
    filter_form = RequestFilterForm(request.GET)

    # Get requests with optional filters
    queryset = Request.objects.all()

    if request.GET.get('status'):
        queryset = queryset.filter(status=request.GET['status'])

    if request.GET.get('priority'):
        queryset = queryset.filter(priority=request.GET['priority'])

    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET['category'])

    if request.GET.get('search'):
        search_term = request.GET['search']
        queryset = queryset.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(requester_name__icontains=search_term)
        )

    # Statistics
    stats = {
        'total_requests': Request.objects.count(),
        'open_requests': Request.objects.filter(status='open').count(),
        'in_progress': Request.objects.filter(status='in_progress').count(),
        'resolved': Request.objects.filter(status='resolved').count(),
        'total_experts': Expert.objects.count(),
        'high_priority': Request.objects.filter(priority__in=['high', 'critical']).count(),
    }

    # Category distribution
    category_stats = Request.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')

    return render(request, 'dashboard.html', {
        'requests': queryset.order_by('-created_at'),
        'filter_form': filter_form,
        'stats': stats,
        'category_stats': category_stats,
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
