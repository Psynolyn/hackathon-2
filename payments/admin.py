"""
Admin configuration for payment models.
"""
from django.contrib import admin
from .models import Plan, Payment


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price_kes', 'duration_days', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('code', 'name', 'price_kes', 'duration_days', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount_kes', 'status', 'provider_reference', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__username', 'user__email', 'provider_reference')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('user', 'plan', 'amount_kes', 'currency', 'status')
        }),
        ('Provider Data', {
            'fields': ('provider_reference', 'checkout_payload', 'webhook_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'plan')