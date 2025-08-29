"""
Views for payment and subscription management.
"""
import logging
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from intasend import APIService
from .models import Plan, Payment
from .serializers import PlanSerializer, PaymentSerializer, CheckoutRequestSerializer

logger = logging.getLogger(__name__)


class PlanListView(generics.ListAPIView):
    """List available subscription plans."""
    
    queryset = Plan.objects.filter(active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List subscription plans",
        description="Get all available subscription plans"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Create payment checkout",
    description="Create IntaSend checkout for premium subscription",
    request=CheckoutRequestSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'payment_id': {'type': 'string'},
                'checkout_url': {'type': 'string'},
                'provider_reference': {'type': 'string'}
            }
        },
        400: {'description': 'Invalid request data'},
        404: {'description': 'Plan not found'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    """Create IntaSend checkout for subscription payment."""
    
    serializer = CheckoutRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    plan_code = serializer.validated_data['plan_code']
    phone = serializer.validated_data['phone']
    email = serializer.validated_data['email']
    
    try:
        # Get plan
        plan = Plan.objects.get(code=plan_code, active=True)
    except Plan.DoesNotExist:
        return Response({
            'detail': f'Plan {plan_code} not found or inactive'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            amount_kes=plan.price_kes,
            status='PENDING'
        )
        
        # Initialize IntaSend service
        service = APIService(
            token=settings.INTASEND_TOKEN,
            publishable_key=settings.INTASEND_PUBLISHABLE_KEY,
            test=settings.INTASEND_TEST_MODE
        )
        
        # Create checkout
        checkout_data = {
            'amount': plan.price_kes,
            'currency': 'KES',
            'email': email,
            'phone_number': phone,
            'api_ref': str(payment.id),
            'redirect_url': f"{request.build_absolute_uri('/')}payment-success/",
            'comment': f"MoodMate {plan.name} Subscription"
        }
        
        checkout_response = service.collect.checkout(**checkout_data)
        
        # Update payment with provider data
        payment.provider_reference = checkout_response.get('id')
        payment.checkout_payload = checkout_response
        payment.save()
        
        return Response({
            'payment_id': str(payment.id),
            'checkout_url': checkout_response.get('url'),
            'provider_reference': checkout_response.get('id'),
            'checkout_data': checkout_response
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error creating checkout: {e}")
        return Response({
            'detail': 'Failed to create checkout. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentListView(generics.ListAPIView):
    """List user's payment history."""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List user payments",
        description="Get current user's payment history"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)