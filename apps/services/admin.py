"""
Admin configuration for services app.
"""

from django.contrib import admin
from .models import ServiceCategory, GarmentType, Service, PricingZone, ServicePricing, Addon


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceCategory model."""

    list_display = ('name', 'slug', 'icon', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'icon', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GarmentType)
class GarmentTypeAdmin(admin.ModelAdmin):
    """Admin configuration for GarmentType model."""

    list_display = ('name', 'slug', 'category', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration for Service model."""

    list_display = ('name', 'category', 'garment', 'turnaround_time', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'turnaround_time', 'created_at')
    search_fields = ('name', 'description', 'garment__name', 'category__name')
    ordering = ('category', 'garment', 'turnaround_time')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('category', 'garment')


@admin.register(PricingZone)
class PricingZoneAdmin(admin.ModelAdmin):
    """Admin configuration for PricingZone model."""

    list_display = ('zone', 'name', 'multiplier', 'created_at')
    search_fields = ('zone', 'name', 'description')
    ordering = ('zone',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServicePricing)
class ServicePricingAdmin(admin.ModelAdmin):
    """Admin configuration for ServicePricing model."""

    list_display = ('service', 'zone', 'base_price', 'discount_price', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'zone', 'valid_from', 'valid_to')
    search_fields = ('service__name', 'zone__zone')
    ordering = ('service', 'zone')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('service', 'zone')


@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    """Admin configuration for Addon model."""

    list_display = ('name', 'slug', 'price_type', 'price', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'price_type', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    readonly_fields = ('created_at', 'updated_at')
