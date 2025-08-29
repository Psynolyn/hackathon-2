"""
Serializers for payment and subscription functionality.
"""
from rest_framework import serializers
from .models import Plan, Payment


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans."""
    
    class Meta:
        model = Plan
        fields = ['code', 'name', 'price_kes', 'duration_days', 'active']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment records."""
    
    user = serializers.StringRelatedField(read_only=True)
    plan = PlanSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'plan', 'amount_kes', 'currency',
            'status', 'provider_reference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CheckoutRequestSerializer(serializers.Serializer):
    """Serializer for checkout request data."""
    
    plan_code = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    
    def validate_phone(self, value):
        """Validate phone number format."""
        # Basic validation for Kenyan phone numbers
        if not value.startswith(('07', '01', '+254')):
            raise serializers.ValidationError("Please provide a valid Kenyan phone number")
        return value