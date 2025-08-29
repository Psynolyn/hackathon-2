"""
URL patterns for payment endpoints.
"""
from django.urls import path
from .views import PlanListView, create_checkout, PaymentListView
from .webhooks import intasend_webhook

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan_list'),
    path('create_checkout/', create_checkout, name='create_checkout'),
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('webhook/', intasend_webhook, name='intasend_webhook'),
]