"""
Admin configuration for user models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'daily_ai_calls', 'premium_expires_at', 'is_premium_active')
    list_filter = ('plan', 'premium_expires_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'is_premium_active', 'remaining_ai_calls')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Subscription', {'fields': ('plan', 'premium_expires_at', 'is_premium_active')}),
        ('AI Usage', {'fields': ('daily_ai_calls', 'remaining_ai_calls', 'last_ai_calls_reset')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)