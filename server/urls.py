from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from server import views

urlpatterns = [
    # Index/Landing pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),

    # Authentication
    path(
        'accounts/login/',
        views.RememberMeLoginView.as_view(),
        name='login',
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),

    # Request management
    path('submit/', views.submit_request, name='submit_request'),
    path('request/<int:request_id>/submitted/', views.request_submitted, name='request_submitted'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('request/<int:request_id>/mark-done/', views.mark_request_done, name='mark_request_done'),
    path('request/<int:request_id>/assign-expert/', views.admin_assign_expert, name='admin_assign_expert'),
    path('request/<int:request_id>/unassign-expert/', views.admin_unassign_expert, name='admin_unassign_expert'),
    path('request/<int:request_id>/leave/', views.leave_assigned_request, name='leave_assigned_request'),
    path('request/<int:request_id>/review/', views.review_request, name='review_request'),
    path('request/<int:request_id>/chat/', views.request_chat, name='request_chat'),

    # Expert directory
    path('experts/', views.expert_directory, name='expert_directory'),
    path('experts/<int:expert_id>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Admin
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-chat/', views.admin_chat, name='admin_chat'),

    # Health check
    path('health/', lambda request: {'status': 'ok'}, name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

