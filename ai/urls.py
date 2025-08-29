"""
URL patterns for AI and music recommendation endpoints.
"""
from django.urls import path
from .views import analyze_emotion, music_recommendations

urlpatterns = [
    path('analyze/', analyze_emotion, name='analyze_emotion'),
    path('recommend/', music_recommendations, name='music_recommendations'),
]