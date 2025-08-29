"""
Admin configuration for mood models.
"""
from django.contrib import admin
from .models import MoodLog


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood', 'intensity', 'detected_emotion', 'detected_confidence', 'created_at')
    list_filter = ('mood', 'intensity', 'detected_emotion', 'created_at')
    search_fields = ('user__username', 'user__email', 'mood', 'note')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'mood', 'intensity', 'note')
        }),
        ('AI Analysis', {
            'fields': ('detected_emotion', 'detected_confidence', 'advice'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')