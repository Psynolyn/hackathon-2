"""
Payment and subscription models for MoodMate backend.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Plan(models.Model):
    """Subscription plan model."""
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_kes = models.IntegerField(help_text="Price in Kenyan Shillings")
    duration_days = models.IntegerField(help_text="Plan duration in days")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plans'
        ordering = ['price_kes']
    
    def __str__(self):
        return f"{self.name} - {self.price_kes} KES"


class Payment(models.Model):
    """Payment transaction model."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount_kes = models.IntegerField()
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    checkout_payload = models.JSONField(blank=True, null=True)
    webhook_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider_reference']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.status}"
    
    def process_success(self):
        """Process successful payment and upgrade user."""
        if self.status == 'SUCCESS':
            return  # Already processed
        
        self.status = 'SUCCESS'
        self.save(update_fields=['status', 'updated_at'])
        
        # Upgrade user to premium
        profile = self.user.profile
        profile.plan = 'PREMIUM'
        
        # Set expiration date
        if profile.premium_expires_at and profile.premium_expires_at > timezone.now():
            # Extend existing subscription
            profile.premium_expires_at += timezone.timedelta(days=self.plan.duration_days)
        else:
            # New subscription
            profile.premium_expires_at = timezone.now() + timezone.timedelta(days=self.plan.duration_days)
        
        # Reset AI calls for premium user
        profile.daily_ai_calls = 0
        profile.save()