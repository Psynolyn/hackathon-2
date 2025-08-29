"""
Webhook handlers for payment processing.
"""
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Payment

logger = logging.getLogger(__name__)


@extend_schema(
    summary="IntaSend webhook",
    description="Webhook endpoint for IntaSend payment status updates",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {'type': 'string'},
                'state': {'type': 'string'},
                'api_ref': {'type': 'string'},
                'amount': {'type': 'number'},
                'currency': {'type': 'string'}
            }
        }
    },
    responses={
        200: {'description': 'Webhook processed successfully'},
        400: {'description': 'Invalid webhook data'},
        404: {'description': 'Payment not found'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def intasend_webhook(request):
    """
    Handle IntaSend webhook notifications for payment status updates.
    """
    try:
        # Parse webhook data
        webhook_data = request.data
        logger.info(f"Received IntaSend webhook: {webhook_data}")
        
        # Extract key fields
        provider_reference = webhook_data.get('id')
        api_ref = webhook_data.get('api_ref')
        state = webhook_data.get('state', '').upper()
        
        if not provider_reference and not api_ref:
            return Response({
                'detail': 'Missing payment reference in webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find payment record
        payment = None
        if api_ref:
            try:
                payment = Payment.objects.get(id=api_ref)
            except Payment.DoesNotExist:
                pass
        
        if not payment and provider_reference:
            try:
                payment = Payment.objects.get(provider_reference=provider_reference)
            except Payment.DoesNotExist:
                pass
        
        if not payment:
            logger.warning(f"Payment not found for webhook: {webhook_data}")
            return Response({
                'detail': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already processed (idempotency)
        if payment.status == 'SUCCESS' and state == 'COMPLETE':
            logger.info(f"Payment {payment.id} already processed successfully")
            return Response({'detail': 'Already processed'}, status=status.HTTP_200_OK)
        
        # Update payment with webhook data
        payment.webhook_data = webhook_data
        
        # Process payment based on state
        if state in ['COMPLETE', 'COMPLETED', 'SUCCESS']:
            payment.process_success()
            logger.info(f"Payment {payment.id} processed successfully")
            
        elif state in ['FAILED', 'CANCELLED', 'EXPIRED']:
            payment.status = 'FAILED'
            payment.save(update_fields=['status', 'webhook_data', 'updated_at'])
            logger.info(f"Payment {payment.id} marked as failed")
        
        else:
            # Update webhook data but keep status as pending
            payment.save(update_fields=['webhook_data', 'updated_at'])
            logger.info(f"Payment {payment.id} status unchanged: {state}")
        
        return Response({
            'detail': 'Webhook processed successfully',
            'payment_id': str(payment.id),
            'status': payment.status
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        return Response({
            'detail': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response({
            'detail': 'Internal server error processing webhook'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)