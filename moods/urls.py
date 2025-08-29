"""
URL patterns for mood tracking endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MoodLogViewSet

router = DefaultRouter()
router.register(r'', MoodLogViewSet, basename='moodlog')

urlpatterns = [
    path('', include(router.urls)),
]