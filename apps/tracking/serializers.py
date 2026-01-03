"""
Serializers for Location Tracking API endpoints.
"""

from rest_framework import serializers
from .models import LocationUpdate, Route, TrackingSession
from apps.orders.models import Order


class LocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for location updates."""

    partner_name = serializers.CharField(source='partner.business_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = LocationUpdate
        fields = [
            'id',
            'order',
            'order_number',
            'partner',
            'partner_name',
            'latitude',
            'longitude',
            'coordinates',
            'accuracy',
            'altitude',
            'speed',
            'heading',
            'address',
            'status',
            'metadata',
            'timestamp',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_coordinates(self, obj):
        """Get coordinates as [longitude, latitude] for map libraries."""
        return [float(obj.longitude), float(obj.latitude)]


class LocationUpdateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating location updates."""

    class Meta:
        model = LocationUpdate
        fields = [
            'order',
            'latitude',
            'longitude',
            'accuracy',
            'altitude',
            'speed',
            'heading',
            'address',
            'status',
            'metadata',
            'timestamp',
        ]

    def validate(self, data):
        """Validate location data."""
        # Ensure partner from request user
        request = self.context.get('request')
        if not hasattr(request.user, 'partner_profile'):
            raise serializers.ValidationError({
                'partner': 'User must be a partner to submit location updates.'
            })

        data['partner'] = request.user.partner_profile
        return data


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for delivery routes."""

    order_number = serializers.CharField(source='order.order_number', read_only=True)
    partner_name = serializers.CharField(source='partner.business_name', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    estimated_arrival_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = [
            'id',
            'order',
            'order_number',
            'partner',
            'partner_name',
            'origin_latitude',
            'origin_longitude',
            'origin_address',
            'destination_latitude',
            'destination_longitude',
            'destination_address',
            'waypoints',
            'encoded_polyline',
            'distance_meters',
            'duration_seconds',
            'estimated_arrival',
            'estimated_arrival_formatted',
            'actual_arrival',
            'started_at',
            'completed_at',
            'is_active',
            'progress_percentage',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'estimated_arrival', 'actual_arrival']

    def get_progress_percentage(self, obj):
        """Calculate delivery progress if there are recent location updates."""
        latest_update = obj.order.location_updates.filter(
            partner=obj.partner
        ).first()

        if latest_update:
            return obj.calculate_progress(
                float(latest_update.latitude),
                float(latest_update.longitude)
            )
        return 0

    def get_estimated_arrival_formatted(self, obj):
        """Format ETA in human-readable format."""
        if obj.estimated_arrival:
            from django.utils.timesince import timeuntil
            return timeuntil(obj.estimated_arrival)
        return None


class TrackingSessionSerializer(serializers.ModelSerializer):
    """Serializer for tracking sessions."""

    order_number = serializers.CharField(source='order.order_number', read_only=True)
    partner_name = serializers.CharField(source='partner.business_name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = TrackingSession
        fields = [
            'id',
            'order',
            'order_number',
            'partner',
            'partner_name',
            'started_at',
            'ended_at',
            'is_active',
            'total_distance_meters',
            'distance_km',
            'total_duration_seconds',
            'duration_formatted',
            'average_speed_kmh',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'started_at',
            'total_distance_meters',
            'total_duration_seconds',
            'average_speed_kmh',
        ]

    def get_duration_formatted(self, obj):
        """Format duration in human-readable format."""
        if obj.total_duration_seconds:
            hours = obj.total_duration_seconds // 3600
            minutes = (obj.total_duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0m"

    def get_distance_km(self, obj):
        """Get distance in kilometers."""
        return round(obj.total_distance_meters / 1000, 2) if obj.total_distance_meters else 0


class GeoJSONSerializer(serializers.Serializer):
    """Serializer for GeoJSON responses."""

    type = serializers.CharField(default='FeatureCollection')
    features = serializers.ListField()
