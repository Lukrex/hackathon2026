from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from server.viewsets import (
    CategoryViewSet, ExpertViewSet, RequestViewSet, ExpertMatchViewSet
)

# REST API Router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'experts', ExpertViewSet, basename='expert')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'matches', ExpertMatchViewSet, basename='match')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # Health check
    path('health/', lambda request: {'status': 'ok'}, name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
