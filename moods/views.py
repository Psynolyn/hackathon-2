"""
Views for mood tracking functionality.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import MoodLog
from .serializers import MoodLogSerializer, MoodLogCreateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List mood logs",
        description="Retrieve paginated list of user's mood logs"
    ),
    create=extend_schema(
        summary="Create mood log",
        description="Create a new mood log entry"
    ),
    retrieve=extend_schema(
        summary="Get mood log",
        description="Retrieve a specific mood log entry"
    ),
    destroy=extend_schema(
        summary="Delete mood log",
        description="Delete a mood log entry"
    ),
)
class MoodLogViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mood log entries."""
    
    serializer_class = MoodLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mood', 'intensity']
    ordering_fields = ['created_at', 'intensity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return mood logs for the current user only."""
        return MoodLog.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return MoodLogCreateSerializer
        return MoodLogSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a mood log."""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new mood log entry."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mood_log = serializer.save(user=request.user)
        
        # Return full serializer with all fields
        response_serializer = MoodLogSerializer(mood_log)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)