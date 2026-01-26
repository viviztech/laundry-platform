"""
Partner management models for LaundryConnect platform.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from decimal import Decimal


class Partner(models.Model):
    """Main partner/vendor model for laundry service providers."""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]

    BUSINESS_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company/Shop'),
        ('franchise', 'Franchise'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner_code = models.CharField(max_length=50, unique=True, db_index=True)

    # User account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partner_profile'
    )

    # Business information
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPE_CHOICES,
        default='individual'
    )
    business_registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    # Contact information
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)

    # Address information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    # Service area
    service_radius = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Service radius in kilometers"
    )
    pricing_zone = models.ForeignKey(
        'services.PricingZone',
        on_delete=models.PROTECT,
        related_name='partners',
        default='A'
    )

    # Capacity and availability
    daily_capacity = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        help_text="Maximum orders per day"
    )
    current_load = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current active orders"
    )

    # Status and verification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_partners'
    )

    # Ratings and performance
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))]
    )
    total_ratings = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Commission and payment
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Commission percentage"
    )

    # Bank details for payment
    bank_name = models.CharField(max_length=100, blank=True)
    account_holder_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)

    # Documents
    business_license = models.FileField(upload_to='partners/documents/', blank=True)
    tax_certificate = models.FileField(upload_to='partners/documents/', blank=True)
    id_proof = models.FileField(upload_to='partners/documents/', blank=True)

    # Additional information
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    onboarded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'partners'
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['partner_code']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['city', 'status']),
            models.Index(fields=['pincode']),
        ]

    def __str__(self):
        return f"{self.business_name} ({self.partner_code})"

    def save(self, *args, **kwargs):
        """Generate partner code if not exists."""
        if not self.partner_code:
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.partner_code = f"LP{date_str}{random_str}"
        super().save(*args, **kwargs)

    @property
    def capacity_utilization(self):
        """Calculate capacity utilization percentage."""
        if self.daily_capacity == 0:
            return 0
        return (self.current_load / self.daily_capacity) * 100

    @property
    def is_available(self):
        """Check if partner can accept new orders."""
        return (
            self.status == 'active' and
            self.is_verified and
            self.current_load < self.daily_capacity
        )


class PartnerServiceArea(models.Model):
    """Defines specific service areas for partners."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='service_areas'
    )

    # Area information
    pincode = models.CharField(max_length=10)
    area_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Additional charges for this area
    extra_delivery_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_service_areas'
        verbose_name = 'Partner Service Area'
        verbose_name_plural = 'Partner Service Areas'
        unique_together = ['partner', 'pincode']
        indexes = [
            models.Index(fields=['pincode', 'is_active']),
        ]

    def __str__(self):
        return f"{self.partner.business_name} - {self.area_name} ({self.pincode})"


class PartnerAvailability(models.Model):
    """Tracks partner availability schedule."""

    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='availability'
    )

    # Schedule
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    is_available = models.BooleanField(default=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_availability'
        verbose_name = 'Partner Availability'
        verbose_name_plural = 'Partner Availability'
        unique_together = ['partner', 'weekday']
        ordering = ['weekday', 'start_time']

    def __str__(self):
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{self.partner.business_name} - {weekday_name} ({self.start_time}-{self.end_time})"


class PartnerHoliday(models.Model):
    """Tracks partner holidays and unavailable dates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='holidays'
    )

    # Holiday details
    date = models.DateField()
    reason = models.CharField(max_length=255)
    is_recurring = models.BooleanField(
        default=False,
        help_text="Recurs annually"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'partner_holidays'
        verbose_name = 'Partner Holiday'
        verbose_name_plural = 'Partner Holidays'
        ordering = ['date']

    def __str__(self):
        return f"{self.partner.business_name} - {self.date} ({self.reason})"


class PartnerPerformance(models.Model):
    """Monthly performance metrics for partners."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )

    # Period
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()

    # Metrics
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    rejected_orders = models.IntegerField(default=0)

    # Revenue
    gross_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    commission_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    net_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Quality metrics
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    on_time_delivery_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Percentage"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_performance'
        verbose_name = 'Partner Performance'
        verbose_name_plural = 'Partner Performance Metrics'
        unique_together = ['partner', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.partner.business_name} - {self.month}/{self.year}"

    @property
    def completion_rate(self):
        """Calculate order completion rate."""
        if self.total_orders == 0:
            return 0
        return (self.completed_orders / self.total_orders) * 100
