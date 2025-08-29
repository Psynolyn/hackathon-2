"""
User models for MoodMate backend.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile with subscription and quota information."""
    
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    premium_expires_at = models.DateTimeField(blank=True, null=True)
    daily_ai_calls = models.IntegerField(default=0)
    last_ai_calls_reset = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"{self.user.username} - {self.plan}"
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active."""
        if self.plan != 'PREMIUM':
            return False
        if not self.premium_expires_at:
            return False
        return timezone.now() < self.premium_expires_at
    
    @property
    def remaining_ai_calls(self):
        """Calculate remaining AI calls for today."""
        from django.conf import settings
        
        if self.is_premium_active:
            max_calls = settings.PREMIUM_DAILY_AI_CALLS
        else:
            max_calls = settings.FREE_DAILY_AI_CALLS
            
        return max(0, max_calls - self.daily_ai_calls)


# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()