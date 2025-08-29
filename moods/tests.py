"""
Tests for mood tracking functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MoodLog


class MoodLogModelTestCase(TestCase):
    """Test MoodLog model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_mood_log_creation(self):
        """Test creating a mood log entry."""
        mood_log = MoodLog.objects.create(
            user=self.user,
            mood='happy',
            intensity=8,
            note='Feeling great today!'
        )
        
        self.assertEqual(mood_log.user, self.user)
        self.assertEqual(mood_log.mood, 'happy')
        self.assertEqual(mood_log.intensity, 8)
        self.assertEqual(mood_log.note, 'Feeling great today!')
    
    def test_mood_log_str_representation(self):
        """Test string representation of mood log."""
        mood_log = MoodLog.objects.create(
            user=self.user,
            mood='stressed',
            intensity=7
        )
        
        expected = f"{self.user.username} - stressed (7/10) - {mood_log.created_at.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(mood_log), expected)


class MoodLogAPITestCase(APITestCase):
    """Test mood log API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create mood logs for both users
        MoodLog.objects.create(user=self.user, mood='happy', intensity=8)
        MoodLog.objects.create(user=self.other_user, mood='sad', intensity=3)
        
        self.client.force_authenticate(user=self.user)
    
    def test_list_mood_logs_authenticated(self):
        """Test listing mood logs returns only user's logs."""
        url = reverse('moodlog-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['mood'], 'happy')
    
    def test_create_mood_log(self):
        """Test creating a new mood log."""
        url = reverse('moodlog-list')
        data = {
            'mood': 'stressed',
            'intensity': 7,
            'note': 'Big presentation tomorrow'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mood'], 'stressed')
        self.assertEqual(response.data['intensity'], 7)
        
        # Check it was saved to database
        mood_log = MoodLog.objects.get(id=response.data['id'])
        self.assertEqual(mood_log.user, self.user)
    
    def test_delete_mood_log(self):
        """Test deleting a mood log."""
        mood_log = MoodLog.objects.create(user=self.user, mood='calm', intensity=5)
        url = reverse('moodlog-detail', kwargs={'pk': mood_log.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check it was deleted
        self.assertFalse(MoodLog.objects.filter(id=mood_log.id).exists())
    
    def test_cannot_access_other_user_mood_logs(self):
        """Test that users cannot access other users' mood logs."""
        other_mood_log = MoodLog.objects.get(user=self.other_user)
        url = reverse('moodlog-detail', kwargs={'pk': other_mood_log.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access mood logs."""
        self.client.force_authenticate(user=None)
        url = reverse('moodlog-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)