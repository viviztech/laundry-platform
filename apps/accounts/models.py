"""
User models for LaundryConnect platform.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the primary identifier."""

    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('partner', 'Partner'),
        ('admin', 'Admin'),
    ]

    # Primary Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, db_index=True)

    # Personal Information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # User Type
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')

    # Status Fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['user_type']),
            models.Index(fields=['-date_joined']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]


class UserProfile(models.Model):
    """Extended user profile information."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)

    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    receive_notifications = models.BooleanField(default=True)
    receive_marketing_emails = models.BooleanField(default=False)

    # Push Notification Token
    fcm_token = models.TextField(blank=True, help_text='Firebase Cloud Messaging token for push notifications')
    fcm_platform = models.CharField(max_length=10, blank=True, choices=[('ios', 'iOS'), ('android', 'Android')])

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(models.Model):
    """User addresses for pickup and delivery."""

    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, choices=ADDRESS_TYPE_CHOICES)

    # Address Details
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, db_index=True)
    country = models.CharField(max_length=100, default='India')

    # Geolocation
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    # Zone for pricing (A, B, C)
    zone = models.CharField(max_length=1, blank=True, db_index=True)

    # Contact Information (optional, different from user)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Metadata
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['pincode']),
            models.Index(fields=['zone']),
        ]

    def __str__(self):
        return f"{self.label} - {self.city}, {self.pincode}"

    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            # Set all other addresses for this user to non-default
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def get_full_address(self):
        """Return the complete formatted address."""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.city, self.state, self.pincode, self.country])
        return ', '.join(parts)
