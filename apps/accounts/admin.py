"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""

    list_display = ('email', 'phone', 'first_name', 'last_name', 'user_type', 'is_active', 'is_verified', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('User Type'), {'fields': ('user_type',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'user_type'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""

    list_display = ('user', 'gender', 'date_of_birth', 'preferred_language', 'receive_notifications')
    list_filter = ('gender', 'preferred_language', 'receive_notifications', 'receive_marketing_emails')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Personal Information'), {'fields': ('profile_image', 'date_of_birth', 'gender')}),
        (_('Preferences'), {'fields': ('preferred_language', 'receive_notifications', 'receive_marketing_emails')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for Address model."""

    list_display = ('user', 'label', 'city', 'pincode', 'zone', 'is_default', 'is_active')
    list_filter = ('label', 'zone', 'is_default', 'is_active', 'city', 'state')
    search_fields = ('user__email', 'address_line1', 'city', 'pincode')
    ordering = ('-is_default', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Address Type'), {'fields': ('label', 'is_default', 'is_active')}),
        (_('Address Details'), {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode', 'country'),
        }),
        (_('Geolocation'), {'fields': ('latitude', 'longitude', 'zone')}),
        (_('Contact Information'), {'fields': ('contact_name', 'contact_phone')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')
