"""
Serializers for accounts app.
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, UserProfile, Address


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = UserProfile
        fields = (
            'profile_image',
            'date_of_birth',
            'gender',
            'preferred_language',
            'receive_notifications',
            'receive_marketing_emails',
        )


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""

    class Meta:
        model = Address
        fields = (
            'id',
            'label',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'pincode',
            'country',
            'latitude',
            'longitude',
            'zone',
            'contact_name',
            'contact_phone',
            'is_default',
            'is_active',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'zone')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    profile = UserProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone',
            'first_name',
            'last_name',
            'user_type',
            'is_active',
            'is_verified',
            'date_joined',
            'profile',
            'addresses',
        )
        read_only_fields = ('id', 'date_joined', 'is_verified')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'password', 'password2', 'first_name', 'last_name', 'user_type')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'user_type': {'required': False},
        }

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        """Validate phone uniqueness."""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        """Create user with encrypted password."""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)

        # Create user profile
        UserProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate credentials and return user."""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'email': 'No user found with this email address.'}
                )

            if not user.check_password(password):
                raise serializers.ValidationError(
                    {'password': 'Incorrect password.'}
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    {'email': 'This account is inactive.'}
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )


class TokenObtainSerializer(serializers.Serializer):
    """Serializer for JWT token response."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate new password confirmation."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "New password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class FCMTokenSerializer(serializers.Serializer):
    """Serializer for registering FCM push notification token."""

    token = serializers.CharField(required=True, max_length=500)
    platform = serializers.ChoiceField(
        required=True,
        choices=[('ios', 'iOS'), ('android', 'Android')]
    )

    def validate_token(self, value):
        """Validate token is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Token cannot be empty.")
        return value.strip()
