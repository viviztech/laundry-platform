"""
Service catalog models for LaundryConnect platform.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ServiceCategory(models.Model):
    """Categories for laundry services (Wash & Fold, Dry Clean, etc.)."""

    CATEGORY_ICONS = [
        ('wash_fold', 'Wash & Fold'),
        ('dry_clean', 'Dry Clean'),
        ('iron_press', 'Iron & Press'),
        ('steam_iron', 'Steam Iron'),
        ('wash_iron', 'Wash & Iron'),
        ('premium', 'Premium Service'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, choices=CATEGORY_ICONS, default='wash_fold')
    image = models.ImageField(upload_to='services/categories/', null=True, blank=True)

    # Display order
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_categories'
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class GarmentType(models.Model):
    """Types of garments (Shirt, Trouser, Dress, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/garments/', null=True, blank=True)

    # Categorization
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='garments'
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'garment_types'
        verbose_name = 'Garment Type'
        verbose_name_plural = 'Garment Types'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Individual services offered (Wash & Fold for Shirt, Dry Clean for Suit, etc.)."""

    TURNAROUND_CHOICES = [
        ('express', 'Express (Same Day)'),
        ('standard', 'Standard (24-48 hours)'),
        ('economy', 'Economy (3-5 days)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )
    garment = models.ForeignKey(
        GarmentType,
        on_delete=models.CASCADE,
        related_name='services'
    )

    # Service details
    name = models.CharField(max_length=200)  # e.g., "Wash & Fold - Shirt"
    description = models.TextField(blank=True)
    turnaround_time = models.CharField(
        max_length=20,
        choices=TURNAROUND_CHOICES,
        default='standard'
    )

    # Metadata
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        unique_together = ['category', 'garment', 'turnaround_time']
        ordering = ['category', 'garment', 'turnaround_time']

    def __str__(self):
        return f"{self.category.name} - {self.garment.name} ({self.get_turnaround_time_display()})"


class PricingZone(models.Model):
    """Pricing zones for location-based pricing (Zone A, B, C)."""

    ZONE_CHOICES = [
        ('A', 'Zone A - Premium'),
        ('B', 'Zone B - Standard'),
        ('C', 'Zone C - Economy'),
    ]

    zone = models.CharField(max_length=1, choices=ZONE_CHOICES, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pricing_zones'
        verbose_name = 'Pricing Zone'
        verbose_name_plural = 'Pricing Zones'
        ordering = ['zone']

    def __str__(self):
        return f"{self.zone} - {self.name}"


class ServicePricing(models.Model):
    """Pricing for services with zone-based variations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='pricing'
    )
    zone = models.ForeignKey(
        PricingZone,
        on_delete=models.CASCADE,
        related_name='pricing'
    )

    # Pricing details
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Validity
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_pricing'
        verbose_name = 'Service Pricing'
        verbose_name_plural = 'Service Pricing'
        unique_together = ['service', 'zone']
        ordering = ['service', 'zone']

    def __str__(self):
        return f"{self.service} - {self.zone} - ₹{self.get_effective_price()}"

    def get_effective_price(self):
        """Return the effective price (discount price if available, otherwise base price)."""
        return self.discount_price if self.discount_price else self.base_price


class Addon(models.Model):
    """Additional add-on services (Fabric Softener, Stain Removal, etc.)."""

    ADDON_TYPE_CHOICES = [
        ('per_item', 'Per Item'),
        ('per_order', 'Per Order'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    # Pricing
    price_type = models.CharField(
        max_length=20,
        choices=ADDON_TYPE_CHOICES,
        default='per_item'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'addons'
        verbose_name = 'Add-on Service'
        verbose_name_plural = 'Add-on Services'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.get_price_type_display()})"
