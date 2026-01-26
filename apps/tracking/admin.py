"""
Django admin configuration for Tracking models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import LocationUpdate, Route, TrackingSession


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    """Admin interface for LocationUpdate model."""

    list_display = [
        'order_link',
        'partner_link',
        'coordinates_display',
        'speed',
        'status',
        'timestamp',
        'is_recent_indicator',
    ]
    list_filter = [
        'status',
        'timestamp',
        'created_at',
    ]
    search_fields = [
        'order__order_number',
        'partner__business_name',
        'address',
    ]
    readonly_fields = [
        'id',
        'order',
        'partner',
        'created_at',
        'updated_at',
        'map_preview',
    ]
    fieldsets = [
        ('Location Information', {
            'fields': ['id', 'order', 'partner', 'timestamp', 'map_preview']
        }),
        ('GPS Data', {
            'fields': [
                ('latitude', 'longitude'),
                ('accuracy', 'altitude'),
                ('speed', 'heading'),
            ]
        }),
        ('Additional Info', {
            'fields': ['address', 'status', 'metadata']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'timestamp'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def partner_link(self, obj):
        """Link to partner."""
        url = reverse('admin:partners_partner_change', args=[obj.partner.id])
        return format_html('<a href="{}">{}</a>', url, obj.partner.business_name)
    partner_link.short_description = 'Partner'

    def coordinates_display(self, obj):
        """Display coordinates."""
        return f"{obj.latitude}, {obj.longitude}"
    coordinates_display.short_description = 'Coordinates'

    def is_recent_indicator(self, obj):
        """Show if location is recent."""
        return obj.is_recent()
    is_recent_indicator.boolean = True
    is_recent_indicator.short_description = 'Recent'

    def map_preview(self, obj):
        """Show map preview link."""
        if obj.latitude and obj.longitude:
            google_maps_url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank">View on Google Maps</a>',
                google_maps_url
            )
        return '-'
    map_preview.short_description = 'Map'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'partner')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """Admin interface for Route model."""

    list_display = [
        'order_link',
        'partner_link',
        'distance_km',
        'duration_formatted',
        'eta_display',
        'is_active',
        'progress_bar',
    ]
    list_filter = [
        'is_active',
        'created_at',
        'started_at',
    ]
    search_fields = [
        'order__order_number',
        'partner__business_name',
        'origin_address',
        'destination_address',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'estimated_arrival',
        'map_link',
    ]
    fieldsets = [
        ('Route Information', {
            'fields': ['id', 'order', 'partner', 'is_active']
        }),
        ('Origin', {
            'fields': [
                ('origin_latitude', 'origin_longitude'),
                'origin_address',
            ]
        }),
        ('Destination', {
            'fields': [
                ('destination_latitude', 'destination_longitude'),
                'destination_address',
            ]
        }),
        ('Route Details', {
            'fields': [
                'waypoints',
                'encoded_polyline',
                ('distance_meters', 'duration_seconds'),
                'map_link',
            ]
        }),
        ('Timeline', {
            'fields': [
                'started_at',
                'estimated_arrival',
                'actual_arrival',
                'completed_at',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'created_at'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def partner_link(self, obj):
        """Link to partner."""
        url = reverse('admin:partners_partner_change', args=[obj.partner.id])
        return format_html('<a href="{}">{}</a>', url, obj.partner.business_name)
    partner_link.short_description = 'Partner'

    def distance_km(self, obj):
        """Display distance in km."""
        if obj.distance_meters:
            return f"{obj.distance_meters / 1000:.2f} km"
        return '-'
    distance_km.short_description = 'Distance'

    def duration_formatted(self, obj):
        """Display duration."""
        if obj.duration_seconds:
            hours = obj.duration_seconds // 3600
            minutes = (obj.duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return '-'
    duration_formatted.short_description = 'Duration'

    def eta_display(self, obj):
        """Display ETA."""
        if obj.estimated_arrival:
            from django.utils.timesince import timeuntil
            return timeuntil(obj.estimated_arrival)
        return '-'
    eta_display.short_description = 'ETA'

    def progress_bar(self, obj):
        """Show progress bar if route has location updates."""
        latest_update = obj.order.location_updates.filter(partner=obj.partner).first()
        if latest_update and obj.distance_meters:
            progress = obj.calculate_progress(
                float(latest_update.latitude),
                float(latest_update.longitude)
            )
            return format_html(
                '<div style="width:100px; background:#f0f0f0; border-radius:3px;">'
                '<div style="width:{}%; background:#28a745; height:20px; border-radius:3px;"></div>'
                '</div>',
                min(100, progress)
            )
        return '-'
    progress_bar.short_description = 'Progress'

    def map_link(self, obj):
        """Link to view route on Google Maps."""
        if obj.origin_latitude and obj.destination_latitude:
            url = (
                f"https://www.google.com/maps/dir/{obj.origin_latitude},{obj.origin_longitude}/"
                f"{obj.destination_latitude},{obj.destination_longitude}"
            )
            return format_html('<a href="{}" target="_blank">View Route on Google Maps</a>', url)
        return '-'
    map_link.short_description = 'Map'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'partner')


@admin.register(TrackingSession)
class TrackingSessionAdmin(admin.ModelAdmin):
    """Admin interface for TrackingSession model."""

    list_display = [
        'order_link',
        'partner_link',
        'started_at',
        'ended_at',
        'is_active',
        'distance_km',
        'duration_formatted',
        'avg_speed',
    ]
    list_filter = [
        'is_active',
        'started_at',
    ]
    search_fields = [
        'order__order_number',
        'partner__business_name',
    ]
    readonly_fields = [
        'id',
        'order',
        'partner',
        'started_at',
        'ended_at',
        'total_distance_meters',
        'total_duration_seconds',
        'average_speed_kmh',
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        ('Session Information', {
            'fields': ['id', 'order', 'partner', 'is_active']
        }),
        ('Timeline', {
            'fields': ['started_at', 'ended_at']
        }),
        ('Statistics', {
            'fields': [
                'total_distance_meters',
                'total_duration_seconds',
                'average_speed_kmh',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'started_at'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def partner_link(self, obj):
        """Link to partner."""
        url = reverse('admin:partners_partner_change', args=[obj.partner.id])
        return format_html('<a href="{}">{}</a>', url, obj.partner.business_name)
    partner_link.short_description = 'Partner'

    def distance_km(self, obj):
        """Display distance in km."""
        return f"{obj.total_distance_meters / 1000:.2f} km" if obj.total_distance_meters else '0 km'
    distance_km.short_description = 'Distance'

    def duration_formatted(self, obj):
        """Display duration."""
        if obj.total_duration_seconds:
            hours = obj.total_duration_seconds // 3600
            minutes = (obj.total_duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return '0m'
    duration_formatted.short_description = 'Duration'

    def avg_speed(self, obj):
        """Display average speed."""
        return f"{obj.average_speed_kmh:.1f} km/h" if obj.average_speed_kmh else '0 km/h'
    avg_speed.short_description = 'Avg Speed'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'partner')
