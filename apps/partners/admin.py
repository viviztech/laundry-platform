"""
Admin configuration for partners app.
"""

from django.contrib import admin
from .models import Partner, PartnerServiceArea, PartnerAvailability, PartnerHoliday, PartnerPerformance


class PartnerServiceAreaInline(admin.TabularInline):
    """Inline admin for partner service areas."""
    model = PartnerServiceArea
    extra = 1
    fields = ('pincode', 'area_name', 'city', 'extra_delivery_charge', 'is_active')


class PartnerAvailabilityInline(admin.TabularInline):
    """Inline admin for partner availability."""
    model = PartnerAvailability
    extra = 0
    fields = ('weekday', 'is_available', 'start_time', 'end_time')


class PartnerHolidayInline(admin.TabularInline):
    """Inline admin for partner holidays."""
    model = PartnerHoliday
    extra = 0
    fields = ('date', 'reason', 'is_recurring')


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin configuration for Partner model."""

    list_display = (
        'partner_code', 'business_name', 'contact_person',
        'city', 'status', 'is_verified', 'average_rating',
        'completed_orders', 'created_at'
    )
    list_filter = (
        'status', 'is_verified', 'business_type',
        'city', 'pricing_zone', 'created_at'
    )
    search_fields = (
        'partner_code', 'business_name', 'contact_person',
        'contact_email', 'contact_phone', 'user__email'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'partner_code', 'average_rating', 'total_ratings',
        'completed_orders', 'cancelled_orders', 'total_revenue',
        'current_load', 'created_at', 'updated_at',
        'verified_at', 'onboarded_at'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'partner_code', 'user', 'status', 'is_verified',
                'verified_by', 'verified_at', 'onboarded_at'
            )
        }),
        ('Business Details', {
            'fields': (
                'business_name', 'business_type',
                'business_registration_number', 'tax_id', 'description'
            )
        }),
        ('Contact Information', {
            'fields': (
                'contact_person', 'contact_email', 'contact_phone', 'alternate_phone'
            )
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state',
                'pincode', 'latitude', 'longitude'
            )
        }),
        ('Service Configuration', {
            'fields': (
                'service_radius', 'pricing_zone', 'daily_capacity',
                'current_load', 'commission_rate'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'average_rating', 'total_ratings', 'completed_orders',
                'cancelled_orders', 'total_revenue'
            )
        }),
        ('Bank Details', {
            'fields': (
                'bank_name', 'account_holder_name', 'account_number',
                'ifsc_code', 'upi_id'
            ),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('business_license', 'tax_certificate', 'id_proof'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    inlines = [PartnerServiceAreaInline, PartnerAvailabilityInline, PartnerHolidayInline]
    list_select_related = ('user', 'pricing_zone')

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.append('user')
        return readonly


@admin.register(PartnerServiceArea)
class PartnerServiceAreaAdmin(admin.ModelAdmin):
    """Admin configuration for PartnerServiceArea model."""

    list_display = (
        'partner', 'area_name', 'pincode', 'city',
        'extra_delivery_charge', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'city', 'created_at')
    search_fields = (
        'partner__business_name', 'area_name', 'pincode', 'city'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('partner',)


@admin.register(PartnerAvailability)
class PartnerAvailabilityAdmin(admin.ModelAdmin):
    """Admin configuration for PartnerAvailability model."""

    list_display = (
        'partner', 'weekday', 'is_available',
        'start_time', 'end_time', 'created_at'
    )
    list_filter = ('weekday', 'is_available', 'created_at')
    search_fields = ('partner__business_name',)
    ordering = ('partner', 'weekday', 'start_time')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('partner',)


@admin.register(PartnerHoliday)
class PartnerHolidayAdmin(admin.ModelAdmin):
    """Admin configuration for PartnerHoliday model."""

    list_display = ('partner', 'date', 'reason', 'is_recurring', 'created_at')
    list_filter = ('is_recurring', 'date', 'created_at')
    search_fields = ('partner__business_name', 'reason')
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    list_select_related = ('partner',)


@admin.register(PartnerPerformance)
class PartnerPerformanceAdmin(admin.ModelAdmin):
    """Admin configuration for PartnerPerformance model."""

    list_display = (
        'partner', 'month', 'year', 'total_orders',
        'completed_orders', 'average_rating', 'gross_revenue',
        'net_revenue'
    )
    list_filter = ('year', 'month', 'created_at')
    search_fields = ('partner__business_name',)
    ordering = ('-year', '-month')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('partner',)

    fieldsets = (
        ('Period', {
            'fields': ('partner', 'month', 'year')
        }),
        ('Order Metrics', {
            'fields': (
                'total_orders', 'completed_orders',
                'cancelled_orders', 'rejected_orders'
            )
        }),
        ('Revenue Metrics', {
            'fields': (
                'gross_revenue', 'commission_paid', 'net_revenue'
            )
        }),
        ('Quality Metrics', {
            'fields': (
                'average_rating', 'on_time_delivery_rate'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
