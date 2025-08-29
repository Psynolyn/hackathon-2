"""
Serializers for mood tracking functionality.
"""
from rest_framework import serializers
from .models import MoodLog


class MoodLogSerializer(serializers.ModelSerializer):
    """Serializer for mood log entries."""
    
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = MoodLog
        fields = [
            'id', 'user', 'mood', 'intensity', 'note',
            'detected_emotion', 'detected_confidence', 'advice',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'detected_emotion', 'detected_confidence', 'advice', 'created_at', 'updated_at']
    
    def validate_note(self, value):
        """Validate note length."""
        if value and len(value) > 1000:
            raise serializers.ValidationError("Note cannot exceed 1000 characters")
        return value


class MoodLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating mood log entries."""
    
    class Meta:
        model = MoodLog
        fields = ['mood', 'intensity', 'note']
    
    def validate_note(self, value):
        """Validate note length."""
        if value and len(value) > 1000:
            raise serializers.ValidationError("Note cannot exceed 1000 characters")
        return value