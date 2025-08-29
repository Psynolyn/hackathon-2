"""
Tests for AI services and views.
"""
import responses
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .services import HFClient, SpotifyRecommendationService


class HFClientTestCase(TestCase):
    """Test Hugging Face client functionality."""
    
    def setUp(self):
        self.hf_client = HFClient()
    
    @responses.activate
    def test_analyze_emotion_success(self):
        """Test successful emotion analysis."""
        # Mock HF API response
        responses.add(
            responses.POST,
            f"{self.hf_client.base_url}/{self.hf_client.emotion_model}",
            json=[[{'label': 'joy', 'score': 0.95}]],
            status=200
        )
        
        result = self.hf_client.analyze_emotion("I'm feeling amazing today!")
        
        self.assertEqual(result['label'], 'joy')
        self.assertEqual(result['score'], 0.95)
        self.assertNotIn('ai_unavailable', result)
    
    def test_analyze_emotion_no_token(self):
        """Test emotion analysis without API token."""
        with patch.object(self.hf_client, 'api_token', None):
            result = self.hf_client.analyze_emotion("Test text")
            
            self.assertEqual(result['label'], 'neutral')
            self.assertTrue(result['ai_unavailable'])
    
    def test_generate_advice(self):
        """Test advice generation."""
        advice = self.hf_client.generate_advice('joy', 'I feel great!')
        
        self.assertIn('positive energy', advice.lower())
        self.assertIn('wellness advice', advice)


class SpotifyRecommendationServiceTestCase(TestCase):
    """Test Spotify recommendation service."""
    
    def setUp(self):
        self.spotify_service = SpotifyRecommendationService()
    
    def test_get_recommendations_happy(self):
        """Test getting recommendations for happy mood."""
        recommendations = self.spotify_service.get_recommendations('happy')
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertIn('title', recommendations[0])
        self.assertIn('url', recommendations[0])
    
    def test_get_recommendations_unknown_mood(self):
        """Test getting recommendations for unknown mood returns calm playlists."""
        recommendations = self.spotify_service.get_recommendations('unknown_mood')
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)


class AIAnalysisAPITestCase(APITestCase):
    """Test AI analysis API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @responses.activate
    def test_analyze_emotion_success(self):
        """Test successful emotion analysis API call."""
        # Mock HF API response
        responses.add(
            responses.POST,
            "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
            json=[[{'label': 'joy', 'score': 0.95}]],
            status=200
        )
        
        url = reverse('analyze_emotion')
        data = {
            'text': "I'm feeling amazing today!",
            'persist': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('emotion', response.data)
        self.assertIn('advice', response.data)
        self.assertIn('music_recommendations', response.data)
        self.assertIn('mood_log_id', response.data)
        
        # Check AI call was incremented
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.daily_ai_calls, 1)
    
    def test_analyze_emotion_quota_exceeded(self):
        """Test AI analysis when quota is exceeded."""
        # Set user to max free calls
        profile = self.user.profile
        profile.daily_ai_calls = settings.FREE_DAILY_AI_CALLS
        profile.save()
        
        url = reverse('analyze_emotion')
        data = {'text': "Test text"}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertIn('Daily AI limit reached', response.data['detail'])
    
    def test_analyze_emotion_missing_text(self):
        """Test analysis without text."""
        url = reverse('analyze_emotion')
        data = {}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_music_recommendations(self):
        """Test music recommendations endpoint."""
        url = reverse('music_recommendations')
        response = self.client.get(url, {'mood': 'happy'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mood'], 'happy')
        self.assertIn('playlists', response.data)
        self.assertIsInstance(response.data['playlists'], list)
    
    def test_music_recommendations_missing_mood(self):
        """Test music recommendations without mood parameter."""
        url = reverse('music_recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)