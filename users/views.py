"""
User views for authentication and profile management.
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, MeSerializer
from drf_spectacular.utils import extend_schema


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user info along with tokens."""
    
    @extend_schema(
        summary="User login",
        description="Authenticate user and return JWT tokens",
        responses={200: {"access": "string", "refresh": "string", "user": MeSerializer}}
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Add user info to response
            user = User.objects.get(username=request.data.get('username'))
            user_serializer = MeSerializer(user)
            response.data['user'] = user_serializer.data
        return response


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="User registration",
        description="Create a new user account",
        responses={201: MeSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user info with tokens
        refresh = RefreshToken.for_user(user)
        user_serializer = MeSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    """Current user profile endpoint."""
    
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get current user profile",
        description="Retrieve current user information including subscription details"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="User logout",
    description="Logout user by blacklisting refresh token",
    request={"refresh": "string"},
    responses={200: {"detail": "string"}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)