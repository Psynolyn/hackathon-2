"""
Mood tracking models for MoodMate backend.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class MoodLog(models.Model):
    """Model for storing user mood entries."""
    
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('stressed', 'Stressed'),
        ('calm', 'Calm'),
        ('excited', 'Excited'),
        ('angry', 'Angry'),
        ('confused', 'Confused'),
        ('energetic', 'Energetic'),
        ('tired', 'Tired'),
        ('content', 'Content'),
        ('frustrated', 'Frustrated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_logs')
    mood = models.CharField(max_length=30, choices=MOOD_CHOICES)
    intensity = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Intensity level from 1 (low) to 10 (high)"
    )
    note = models.TextField(blank=True, null=True, max_length=1000)
    
    # AI-detected emotion data
    detected_emotion = models.CharField(max_length=50, blank=True, null=True)
    detected_confidence = models.FloatField(blank=True, null=True)
    advice = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mood_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['mood']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.mood} ({self.intensity}/10) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"