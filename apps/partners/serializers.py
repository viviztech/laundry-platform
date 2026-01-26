"""
Serializers for partners app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Partner, PartnerServiceArea, PartnerAvailability, PartnerHoliday, PartnerPerformance
from apps.services.serializers import PricingZoneSerializer

User = get_user_model()


class PartnerServiceAreaSerializer(serializers.ModelSerializer):
    """Serializer for PartnerServiceArea model."""

    class Meta:
        model = PartnerServiceArea
        fields = (
            'id', 'pincode', 'area_name', 'city',
            'is_active', 'extra_delivery_charge',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PartnerAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for PartnerAvailability model."""

    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = PartnerAvailability
        fields = (
            'id', 'weekday', 'weekday_display', 'is_available',
            'start_time', 'end_time', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PartnerHolidaySerializer(serializers.ModelSerializer):
    """Serializer for PartnerHoliday model."""

    class Meta:
        model = PartnerHoliday
        fields = (
            'id', 'date', 'reason', 'is_recurring', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class PartnerPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for PartnerPerformance model."""

    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = PartnerPerformance
        fields = (
            'id', 'month', 'year',
            'total_orders', 'completed_orders', 'cancelled_orders', 'rejected_orders',
            'gross_revenue', 'commission_paid', 'net_revenue',
            'average_rating', 'on_time_delivery_rate', 'completion_rate',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_completion_rate(self, obj):
        """Return order completion rate."""
        return obj.completion_rate


class PartnerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing partners."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    zone_name = serializers.CharField(source='pricing_zone.name', read_only=True)
    capacity_utilization = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = (
            'id', 'partner_code', 'business_name', 'user_email',
            'city', 'status', 'is_verified', 'average_rating',
            'zone_name', 'daily_capacity', 'current_load',
            'capacity_utilization', 'is_available', 'created_at'
        )

    def get_capacity_utilization(self, obj):
        """Return capacity utilization percentage."""
        return obj.capacity_utilization

    def get_is_available(self, obj):
        """Return availability status."""
        return obj.is_available


class PartnerSerializer(serializers.ModelSerializer):
    """Detailed serializer for Partner model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    zone_details = PricingZoneSerializer(source='pricing_zone', read_only=True)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True)

    service_areas = PartnerServiceAreaSerializer(many=True, read_only=True)
    availability = PartnerAvailabilitySerializer(many=True, read_only=True)
    holidays = PartnerHolidaySerializer(many=True, read_only=True)

    capacity_utilization = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = (
            'id', 'partner_code', 'user', 'user_email',
            'business_name', 'business_type', 'business_registration_number', 'tax_id',
            'contact_person', 'contact_email', 'contact_phone', 'alternate_phone',
            'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'latitude', 'longitude',
            'service_radius', 'pricing_zone', 'zone_details',
            'daily_capacity', 'current_load', 'capacity_utilization',
            'status', 'is_verified', 'verified_at', 'verified_by', 'verified_by_email',
            'average_rating', 'total_ratings', 'completed_orders', 'cancelled_orders', 'total_revenue',
            'commission_rate',
            'bank_name', 'account_holder_name', 'account_number', 'ifsc_code', 'upi_id',
            'business_license', 'tax_certificate', 'id_proof',
            'description', 'is_available',
            'service_areas', 'availability', 'holidays',
            'created_at', 'updated_at', 'onboarded_at'
        )
        read_only_fields = (
            'id', 'partner_code', 'user', 'average_rating', 'total_ratings',
            'completed_orders', 'cancelled_orders', 'total_revenue',
            'current_load', 'verified_at', 'verified_by',
            'created_at', 'updated_at', 'onboarded_at'
        )
        extra_kwargs = {
            'account_number': {'write_only': True},
            'ifsc_code': {'write_only': True},
        }

    def get_capacity_utilization(self, obj):
        """Return capacity utilization percentage."""
        return obj.capacity_utilization

    def get_is_available(self, obj):
        """Return availability status."""
        return obj.is_available


class PartnerRegistrationSerializer(serializers.Serializer):
    """Serializer for partner registration."""

    # User account
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)

    # Business information
    business_name = serializers.CharField(max_length=255)
    business_type = serializers.ChoiceField(choices=Partner.BUSINESS_TYPE_CHOICES)
    business_registration_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tax_id = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Contact information
    contact_person = serializers.CharField(max_length=255)
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField(max_length=20)
    alternate_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Address information
    address_line1 = serializers.CharField(max_length=255)
    address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=10)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)

    # Service configuration
    service_radius = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    daily_capacity = serializers.IntegerField(required=False)

    # Description
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Check if email is already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_contact_email(self, value):
        """Validate contact email format."""
        return value


class UpdatePartnerStatusSerializer(serializers.Serializer):
    """Serializer for updating partner status."""

    status = serializers.ChoiceField(choices=Partner.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        """Validate status transition."""
        partner = self.context.get('partner')
        if not partner:
            return value

        # Define valid status transitions
        valid_transitions = {
            'pending': ['active', 'rejected'],
            'active': ['inactive', 'suspended'],
            'inactive': ['active', 'suspended'],
            'suspended': ['active', 'inactive'],
            'rejected': [],  # Cannot change from rejected
        }

        if value not in valid_transitions.get(partner.status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {partner.status} to {value}."
            )
        return value


class PartnerVerificationSerializer(serializers.Serializer):
    """Serializer for partner verification."""

    is_verified = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)
