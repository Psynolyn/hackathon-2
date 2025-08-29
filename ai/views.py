"""
AI-powered views for emotion analysis and music recommendations.
"""
import logging
from datetime import date
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .services import HFClient, SpotifyRecommendationService
from moods.models import MoodLog

logger = logging.getLogger(__name__)


def ensure_daily_reset(user):
    """
    Ensure user's daily AI calls are reset if it's a new day.
    
    Args:
        user: User instance
    """
    profile = user.profile
    today = date.today()
    
    if not profile.last_ai_calls_reset or profile.last_ai_calls_reset < today:
        profile.daily_ai_calls = 0
        profile.last_ai_calls_reset = today
        profile.save(update_fields=['daily_ai_calls', 'last_ai_calls_reset'])


def check_ai_quota(user):
    """
    Check if user has remaining AI calls for today.
    
    Args:
        user: User instance
        
    Returns:
        Tuple of (has_quota: bool, error_response: Response or None)
    """
    ensure_daily_reset(user)
    profile = user.profile
    
    # Determine quota based on plan
    if profile.is_premium_active:
        max_calls = settings.PREMIUM_DAILY_AI_CALLS
    else:
        max_calls = settings.FREE_DAILY_AI_CALLS
    
    if profile.daily_ai_calls >= max_calls:
        error_response = Response({
            'detail': 'Daily AI limit reached. Upgrade to Premium for more calls.',
            'current_calls': profile.daily_ai_calls,
            'max_calls': max_calls,
            'plan': profile.plan
        }, status=status.HTTP_402_PAYMENT_REQUIRED)
        return False, error_response
    
    return True, None


def increment_ai_calls(user):
    """
    Increment user's daily AI call count.
    
    Args:
        user: User instance
    """
    with transaction.atomic():
        profile = user.profile
        profile.daily_ai_calls += 1
        profile.save(update_fields=['daily_ai_calls'])


@extend_schema(
    summary="Analyze emotion in text",
    description="Analyze emotion in provided text using AI and return emotion, confidence, advice, and music recommendations",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': 'Text to analyze'},
                'mood': {'type': 'string', 'description': 'Optional user-reported mood'},
                'persist': {'type': 'boolean', 'description': 'Whether to save as mood log entry', 'default': False}
            },
            'required': ['text']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'emotion': {
                    'type': 'object',
                    'properties': {
                        'label': {'type': 'string'},
                        'score': {'type': 'number'}
                    }
                },
                'advice': {'type': 'string'},
                'music_recommendations': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'url': {'type': 'string'}
                        }
                    }
                },
                'disclaimer': {'type': 'string'}
            }
        },
        402: {'description': 'AI quota exceeded'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def analyze_emotion(request):
    """Analyze emotion in text and provide recommendations."""
    
    # Check AI quota
    has_quota, error_response = check_ai_quota(request.user)
    if not has_quota:
        return error_response
    
    # Get request data
    text = request.data.get('text', '').strip()
    user_mood = request.data.get('mood')
    persist = request.data.get('persist', False)
    
    if not text:
        return Response({
            'detail': 'Text is required for analysis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(text) > 1000:
        return Response({
            'detail': 'Text cannot exceed 1000 characters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Analyze emotion
        hf_client = HFClient()
        emotion_result = hf_client.analyze_emotion(text)
        
        # Generate advice
        advice = hf_client.generate_advice(emotion_result['label'], text)
        
        # Get music recommendations
        spotify_service = SpotifyRecommendationService()
        music_recommendations = spotify_service.get_recommendations(emotion_result['label'])
        
        # Increment AI call count
        increment_ai_calls(request.user)
        
        # Optionally persist as mood log
        mood_log = None
        if persist:
            mood_log = MoodLog.objects.create(
                user=request.user,
                mood=user_mood or emotion_result['label'],
                intensity=min(10, max(1, int(emotion_result['score'] * 10))),
                note=text[:1000],  # Truncate if needed
                detected_emotion=emotion_result['label'],
                detected_confidence=emotion_result['score'],
                advice=advice
            )
        
        response_data = {
            'emotion': {
                'label': emotion_result['label'],
                'score': emotion_result['score']
            },
            'advice': advice,
            'music_recommendations': music_recommendations,
            'disclaimer': 'This is general wellness advice and not a substitute for professional mental health support.',
            'ai_unavailable': emotion_result.get('ai_unavailable', False)
        }
        
        if mood_log:
            response_data['mood_log_id'] = str(mood_log.id)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in emotion analysis: {e}")
        return Response({
            'detail': 'An error occurred during analysis. Please try again.',
            'ai_unavailable': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get music recommendations",
    description="Get curated music playlist recommendations based on mood",
    parameters=[
        OpenApiParameter(
            name='mood',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Mood for music recommendations',
            required=True
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'mood': {'type': 'string'},
                'playlists': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'url': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def music_recommendations(request):
    """Get music recommendations based on mood."""
    
    mood = request.query_params.get('mood')
    if not mood:
        return Response({
            'detail': 'Mood parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        spotify_service = SpotifyRecommendationService()
        playlists = spotify_service.get_recommendations(mood)
        
        return Response({
            'mood': mood,
            'playlists': playlists
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting music recommendations: {e}")
        return Response({
            'detail': 'An error occurred getting recommendations. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)