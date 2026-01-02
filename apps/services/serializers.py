"""
Serializers for services app.
"""

from rest_framework import serializers
from .models import ServiceCategory, GarmentType, Service, PricingZone, ServicePricing, Addon


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for ServiceCategory model."""

    class Meta:
        model = ServiceCategory
        fields = (
            'id', 'name', 'slug', 'description', 'icon',
            'image', 'display_order', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class GarmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for GarmentType model."""

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = GarmentType
        fields = (
            'id', 'name', 'slug', 'description', 'image',
            'category', 'category_name', 'display_order',
            'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class PricingZoneSerializer(serializers.ModelSerializer):
    """Serializer for PricingZone model."""

    class Meta:
        model = PricingZone
        fields = ('zone', 'name', 'description', 'multiplier', 'created_at')
        read_only_fields = ('created_at',)


class ServicePricingSerializer(serializers.ModelSerializer):
    """Serializer for ServicePricing model."""

    zone_name = serializers.CharField(source='zone.name', read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_effective_price'
    )

    class Meta:
        model = ServicePricing
        fields = (
            'id', 'service', 'zone', 'zone_name',
            'base_price', 'discount_price', 'effective_price',
            'valid_from', 'valid_to', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    garment_name = serializers.CharField(source='garment.name', read_only=True)
    pricing = ServicePricingSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            'id', 'category', 'category_name', 'garment', 'garment_name',
            'name', 'description', 'turnaround_time', 'is_active',
            'pricing', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing services."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    garment_name = serializers.CharField(source='garment.name', read_only=True)

    class Meta:
        model = Service
        fields = (
            'id', 'category_name', 'garment_name',
            'name', 'turnaround_time', 'is_active'
        )


class AddonSerializer(serializers.ModelSerializer):
    """Serializer for Addon model."""

    class Meta:
        model = Addon
        fields = (
            'id', 'name', 'slug', 'description', 'icon',
            'price_type', 'price', 'display_order',
            'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ServiceCatalogSerializer(serializers.Serializer):
    """Complete service catalog with all information."""

    categories = ServiceCategorySerializer(many=True, read_only=True)
    garments = GarmentTypeSerializer(many=True, read_only=True)
    services = ServiceListSerializer(many=True, read_only=True)
    addons = AddonSerializer(many=True, read_only=True)
    zones = PricingZoneSerializer(many=True, read_only=True)
