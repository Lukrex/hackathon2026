from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from server.viewsets import (
    CategoryViewSet, ExpertViewSet, RequestViewSet, ExpertMatchViewSet
)
from server import views

# REST API Router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'experts', ExpertViewSet, basename='expert')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'matches', ExpertMatchViewSet, basename='match')

urlpatterns = [
    # Index/Landing pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('api-docs/', views.api_docs, name='api_docs'),

    # Request management
    path('submit/', views.submit_request, name='submit_request'),
    path('request/<int:request_id>/submitted/', views.request_submitted, name='request_submitted'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('request/<int:request_id>/review/', views.review_request, name='review_request'),

    # Expert directory
    path('experts/', views.expert_directory, name='expert_directory'),

    # Admin
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),

    # API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # Health check
    path('health/', lambda request: {'status': 'ok'}, name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

