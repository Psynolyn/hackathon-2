"""
Seed script to create demo data for MoodMate backend.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moodmate_backend.settings')
django.setup()

from django.contrib.auth.models import User
from payments.models import Plan
from moods.models import MoodLog


def create_plans():
    """Create default subscription plans."""
    plans_data = [
        {
            'code': 'FREE',
            'name': 'Free Plan',
            'price_kes': 0,
            'duration_days': 365,  # Permanent
            'active': True
        },
        {
            'code': 'PREMIUM_MONTHLY',
            'name': 'Premium Monthly',
            'price_kes': 499,
            'duration_days': 30,
            'active': True
        },
        {
            'code': 'PREMIUM_YEARLY',
            'name': 'Premium Yearly',
            'price_kes': 4999,
            'duration_days': 365,
            'active': True
        }
    ]
    
    for plan_data in plans_data:
        plan, created = Plan.objects.get_or_create(
            code=plan_data['code'],
            defaults=plan_data
        )
        if created:
            print(f"Created plan: {plan.name}")
        else:
            print(f"Plan already exists: {plan.name}")


def create_demo_user():
    """Create demo user with sample data."""
    # Create demo user
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@demo.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('password')
        user.save()
        print(f"Created demo user: {user.username}")
    else:
        print(f"Demo user already exists: {user.username}")
    
    return user


def create_sample_mood_logs(user):
    """Create sample mood logs for demo user."""
    # Clear existing mood logs for demo user
    MoodLog.objects.filter(user=user).delete()
    
    # Sample mood data for the last 14 days
    sample_moods = [
        ('happy', 8, 'Had a great day at work!'),
        ('stressed', 6, 'Lots of deadlines coming up'),
        ('calm', 7, 'Nice evening walk in the park'),
        ('anxious', 4, 'Worried about the presentation tomorrow'),
        ('excited', 9, 'Got promoted at work!'),
        ('tired', 3, 'Stayed up too late watching movies'),
        ('content', 7, 'Peaceful Sunday morning'),
        ('frustrated', 5, 'Traffic was terrible today'),
        ('energetic', 8, 'Great workout session'),
        ('sad', 4, 'Missing family back home'),
        ('confused', 5, 'Not sure about career direction'),
        ('angry', 6, 'Disagreement with colleague'),
        ('happy', 9, 'Surprise visit from old friend'),
        ('calm', 8, 'Meditation session went well'),
    ]
    
    # Create mood logs spread over last 14 days
    for i, (mood, intensity, note) in enumerate(sample_moods):
        created_at = timezone.now() - timedelta(days=13-i, hours=i*2)
        
        mood_log = MoodLog.objects.create(
            user=user,
            mood=mood,
            intensity=intensity,
            note=note,
            created_at=created_at
        )
        
        # Add some AI analysis data to a few entries
        if i % 3 == 0:
            mood_log.detected_emotion = mood
            mood_log.detected_confidence = 0.85 + (i * 0.01)
            mood_log.advice = f"Based on your {mood} mood, consider taking time for self-care."
            mood_log.save()
    
    print(f"Created {len(sample_moods)} sample mood logs for {user.username}")


def main():
    """Main function to run all seeding operations."""
    print("Starting demo data seeding...")
    
    # Create plans
    create_plans()
    
    # Create demo user
    demo_user = create_demo_user()
    
    # Create sample mood logs
    create_sample_mood_logs(demo_user)
    
    print("\nDemo data seeding completed!")
    print("\nDemo credentials:")
    print("Username: demo")
    print("Password: password")
    print("Email: demo@demo.com")
    print("\nYou can now:")
    print("1. Login with demo credentials")
    print("2. View sample mood logs")
    print("3. Test AI analysis endpoints")
    print("4. Test payment checkout (test mode)")


if __name__ == '__main__':
    main()