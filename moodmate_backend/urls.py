"""
URL configuration for moodmate_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/users/', include('users.urls')),
    path('api/moods/', include('moods.urls')),
    path('api/ai/', include('ai.urls')),
    path('api/music/', include('ai.urls')),
    path('api/payments/', include('payments.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]