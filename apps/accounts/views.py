"""
API views for accounts app.
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User, UserProfile, Address
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    TokenObtainSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    UserProfileSerializer,
    FCMTokenSerializer,
)


@extend_schema_view(
    post=extend_schema(
        summary="Register new user",
        description="Create a new user account with email and password.",
        request=RegisterSerializer,
        responses={
            201: TokenObtainSerializer,
            400: {'description': 'Validation error'},
        },
    )
)
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """Create user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user data
        user_serializer = UserSerializer(user)

        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        summary="Login user",
        description="Authenticate user and return JWT tokens.",
        request=LoginSerializer,
        responses={
            200: TokenObtainSerializer,
            400: {'description': 'Invalid credentials'},
        },
    )
)
class LoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Update last login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user data
        user_serializer = UserSerializer(user)

        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Logout user",
        description="Blacklist the refresh token to log out the user.",
        responses={
            205: {'description': 'Successfully logged out'},
            400: {'description': 'Bad request'},
        },
    )
)
class LogoutView(APIView):
    """
    API endpoint for user logout.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """Blacklist refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        summary="Get current user",
        description="Retrieve the currently authenticated user's information.",
        responses={200: UserSerializer},
    ),
    put=extend_schema(
        summary="Update current user",
        description="Update the currently authenticated user's information.",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        summary="Partially update current user",
        description="Partially update the currently authenticated user's information.",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
)
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update current user.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user


@extend_schema_view(
    post=extend_schema(
        summary="Change password",
        description="Change the current user's password.",
        request=ChangePasswordSerializer,
        responses={
            200: {'description': 'Password changed successfully'},
            400: {'description': 'Validation error'},
        },
    )
)
class ChangePasswordView(APIView):
    """
    API endpoint for changing password.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Set new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(
        summary="List user addresses",
        description="List all addresses for the current user.",
        responses={200: AddressSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create address",
        description="Create a new address for the current user.",
        request=AddressSerializer,
        responses={201: AddressSerializer},
    ),
)
class AddressListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Return addresses for the current user."""
        return Address.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        """Set the user to the current authenticated user."""
        instance = serializer.save(user=self.request.user)

        if instance.is_default:
            # Unset all other default addresses for this user
            Address.objects.filter(user=self.request.user, is_default=True).exclude(pk=instance.pk).update(is_default=False)


@extend_schema_view(
    get=extend_schema(
        summary="Get address",
        description="Retrieve a specific address.",
        responses={200: AddressSerializer},
    ),
    put=extend_schema(
        summary="Update address",
        description="Update a specific address.",
        request=AddressSerializer,
        responses={200: AddressSerializer},
    ),
    patch=extend_schema(
        summary="Partially update address",
        description="Partially update a specific address.",
        request=AddressSerializer,
        responses={200: AddressSerializer},
    ),
    delete=extend_schema(
        summary="Delete address",
        description="Mark an address as inactive.",
        responses={204: {'description': 'Address deleted'}},
    ),
)
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, and delete an address.
    """
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Return addresses for the current user."""
        return Address.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete: mark as inactive instead of deleting."""
        instance.is_active = False
        instance.save()

    def perform_update(self, serializer):
        """When setting is_default to True, unset all other default addresses."""
        instance = serializer.save()

        if instance.is_default:
            # Unset all other default addresses for this user
            Address.objects.filter(user=self.request.user, is_default=True).exclude(pk=instance.pk).update(is_default=False)


@extend_schema(
    summary="Register FCM token",
    description="Register or update Firebase Cloud Messaging token for push notifications.",
    request=FCMTokenSerializer,
    responses={
        200: {'description': 'Token registered successfully'},
        400: {'description': 'Validation error'},
    },
)
class RegisterFCMTokenView(APIView):
    """
    API endpoint to register FCM push notification token.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """Register or update FCM token for the current user."""
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update FCM token
        profile.fcm_token = serializer.validated_data['token']
        profile.fcm_platform = serializer.validated_data['platform']
        profile.save(update_fields=['fcm_token', 'fcm_platform'])

        return Response(
            {
                "message": "FCM token registered successfully.",
                "platform": profile.fcm_platform
            },
            status=status.HTTP_200_OK
        )
