"""
Location tracking models for LaundryConnect platform.

This module provides real-time GPS tracking for delivery partners.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.orders.models import Order
from apps.partners.models import Partner


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LocationUpdate(BaseModel):
    """
    GPS location updates from delivery partners.

    Tracks partner location during order pickup and delivery.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='location_updates',
        help_text="Order being tracked"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='location_updates',
        help_text="Partner delivering the order"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="GPS latitude (-90 to 90)"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="GPS longitude (-180 to 180)"
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    altitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Altitude in meters"
    )
    speed = models.FloatField(
        null=True,
        blank=True,
        help_text="Speed in km/h"
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Direction in degrees (0-360)"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        help_text="Reverse geocoded address"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('idle', 'Idle'),
            ('picking_up', 'Picking Up'),
            ('in_transit', 'In Transit'),
            ('delivering', 'Delivering'),
            ('completed', 'Completed'),
        ],
        default='idle',
        help_text="Current delivery status"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional tracking data (battery, network, etc.)"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When location was captured"
    )

    class Meta:
        db_table = 'location_updates'
        ordering = ['-timestamp']
        verbose_name = 'Location Update'
        verbose_name_plural = 'Location Updates'
        indexes = [
            models.Index(fields=['order', '-timestamp']),
            models.Index(fields=['partner', '-timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.partner.business_name} - Order #{self.order.order_number} @ {self.timestamp}"

    def get_coordinates(self):
        """Get coordinates as tuple."""
        return (float(self.latitude), float(self.longitude))

    def distance_to(self, lat, lon):
        """
        Calculate distance to another point using Haversine formula.
        Returns distance in kilometers.
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in km

        lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lon2 = radians(lat), radians(lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def is_recent(self, seconds=300):
        """Check if location update is recent (default 5 minutes)."""
        return timezone.now() - self.timestamp < timedelta(seconds=seconds)

    def to_geojson(self):
        """Convert to GeoJSON format for mapping libraries."""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(self.longitude), float(self.latitude)]
            },
            'properties': {
                'id': str(self.id),
                'order_id': str(self.order.id),
                'order_number': self.order.order_number,
                'partner_id': str(self.partner.id),
                'partner_name': self.partner.business_name,
                'status': self.status,
                'speed': self.speed,
                'heading': self.heading,
                'accuracy': self.accuracy,
                'timestamp': self.timestamp.isoformat(),
                'address': self.address,
            }
        }


class Route(BaseModel):
    """
    Planned route for order delivery.

    Stores the expected route from pickup to delivery location.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='route',
        help_text="Order for this route"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='routes',
        help_text="Partner assigned to this route"
    )
    origin_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Starting point latitude"
    )
    origin_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Starting point longitude"
    )
    origin_address = models.CharField(
        max_length=500,
        help_text="Starting address"
    )
    destination_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Destination latitude"
    )
    destination_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Destination longitude"
    )
    destination_address = models.CharField(
        max_length=500,
        help_text="Destination address"
    )
    waypoints = models.JSONField(
        default=list,
        blank=True,
        help_text="Intermediate waypoints [(lat, lon), ...]"
    )
    encoded_polyline = models.TextField(
        blank=True,
        help_text="Encoded polyline from Google Maps"
    )
    distance_meters = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total route distance in meters"
    )
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated duration in seconds"
    )
    estimated_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Estimated arrival time"
    )
    actual_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual arrival time"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When partner started the route"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When route was completed"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether route is currently active"
    )

    class Meta:
        db_table = 'routes'
        ordering = ['-created_at']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['partner', '-created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Route for Order #{self.order.order_number}"

    def get_origin(self):
        """Get origin coordinates as tuple."""
        return (float(self.origin_latitude), float(self.origin_longitude))

    def get_destination(self):
        """Get destination coordinates as tuple."""
        return (float(self.destination_latitude), float(self.destination_longitude))

    def calculate_progress(self, current_lat, current_lon):
        """
        Calculate delivery progress percentage based on current location.
        Returns value between 0 and 100.
        """
        if not self.distance_meters:
            return 0

        # Distance from origin to current location
        from math import radians, sin, cos, sqrt, atan2

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth's radius in meters
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        traveled = haversine(
            float(self.origin_latitude),
            float(self.origin_longitude),
            current_lat,
            current_lon
        )

        progress = (traveled / self.distance_meters) * 100
        return min(100, max(0, progress))  # Clamp between 0-100

    def update_eta(self, current_lat, current_lon, current_speed_kmh):
        """
        Update estimated arrival time based on current location and speed.
        """
        if not self.distance_meters or not current_speed_kmh or current_speed_kmh == 0:
            return None

        from math import radians, sin, cos, sqrt, atan2

        # Calculate remaining distance
        R = 6371000  # Earth's radius in meters
        lat1, lon1 = radians(current_lat), radians(current_lon)
        lat2, lon2 = radians(float(self.destination_latitude)), radians(float(self.destination_longitude))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        remaining_meters = R * c

        # Calculate ETA
        speed_mps = (current_speed_kmh * 1000) / 3600  # Convert km/h to m/s
        remaining_seconds = remaining_meters / speed_mps

        self.estimated_arrival = timezone.now() + timedelta(seconds=remaining_seconds)
        self.save(update_fields=['estimated_arrival'])

        return self.estimated_arrival

    def to_geojson(self):
        """Convert route to GeoJSON format."""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [float(self.origin_longitude), float(self.origin_latitude)],
                    *[[wp[1], wp[0]] for wp in self.waypoints],
                    [float(self.destination_longitude), float(self.destination_latitude)]
                ]
            },
            'properties': {
                'id': str(self.id),
                'order_id': str(self.order.id),
                'order_number': self.order.order_number,
                'distance_meters': self.distance_meters,
                'duration_seconds': self.duration_seconds,
                'is_active': self.is_active,
            }
        }


class TrackingSession(BaseModel):
    """
    Tracking session for an order.

    Groups location updates into discrete tracking sessions.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tracking_sessions',
        help_text="Order being tracked"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='tracking_sessions',
        help_text="Partner being tracked"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When tracking started"
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When tracking ended"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether session is active"
    )
    total_distance_meters = models.FloatField(
        default=0,
        help_text="Total distance covered in meters"
    )
    total_duration_seconds = models.IntegerField(
        default=0,
        help_text="Total duration in seconds"
    )
    average_speed_kmh = models.FloatField(
        default=0,
        help_text="Average speed in km/h"
    )

    class Meta:
        db_table = 'tracking_sessions'
        ordering = ['-started_at']
        verbose_name = 'Tracking Session'
        verbose_name_plural = 'Tracking Sessions'
        indexes = [
            models.Index(fields=['order', '-started_at']),
            models.Index(fields=['partner', '-started_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Tracking Session for Order #{self.order.order_number}"

    def end_session(self):
        """End the tracking session and calculate statistics."""
        self.is_active = False
        self.ended_at = timezone.now()

        # Calculate total distance and duration
        updates = self.order.location_updates.filter(
            created_at__gte=self.started_at,
            created_at__lte=self.ended_at
        ).order_by('timestamp')

        if updates.count() > 1:
            total_distance = 0
            prev_update = None

            for update in updates:
                if prev_update:
                    total_distance += prev_update.distance_to(
                        float(update.latitude),
                        float(update.longitude)
                    )
                prev_update = update

            self.total_distance_meters = total_distance * 1000  # Convert km to meters

        # Calculate duration
        if self.ended_at and self.started_at:
            self.total_duration_seconds = int((self.ended_at - self.started_at).total_seconds())

        # Calculate average speed
        if self.total_duration_seconds > 0:
            hours = self.total_duration_seconds / 3600
            km = self.total_distance_meters / 1000
            self.average_speed_kmh = km / hours

        self.save()
