"""
Analytics models for business intelligence and reporting.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class DailyRevenueSummary(models.Model):
    """
    Daily aggregated revenue metrics.

    Auto-generated daily to cache revenue calculations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True, db_index=True)

    # Revenue metrics
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    order_count = models.IntegerField(default=0)
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Revenue by payment method
    cash_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    card_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    wallet_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    online_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Order status breakdown
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    pending_orders = models.IntegerField(default=0)

    # Customer metrics
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)

    # Refund metrics
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    refund_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_revenue_summaries'
        verbose_name = 'Daily Revenue Summary'
        verbose_name_plural = 'Daily Revenue Summaries'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['date', 'total_revenue']),
        ]

    def __str__(self):
        return f"Revenue Summary - {self.date}: ${self.total_revenue}"

    @property
    def net_revenue(self):
        """Net revenue after refunds."""
        return self.total_revenue - self.refund_amount

    @property
    def cancellation_rate(self):
        """Percentage of cancelled orders."""
        if self.order_count == 0:
            return 0
        return (self.cancelled_orders / self.order_count) * 100


class PartnerPerformanceMetric(models.Model):
    """
    Partner performance KPIs tracked daily.

    Tracks partner efficiency, quality, and revenue metrics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.CASCADE,
        related_name='analytics_performance_metrics'
    )
    date = models.DateField(db_index=True)

    # Order metrics
    orders_received = models.IntegerField(default=0)
    orders_accepted = models.IntegerField(default=0)
    orders_rejected = models.IntegerField(default=0)
    orders_completed = models.IntegerField(default=0)
    orders_cancelled = models.IntegerField(default=0)

    # Revenue metrics
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Timing metrics (in minutes)
    avg_acceptance_time = models.IntegerField(null=True, blank=True)  # Time to accept order
    avg_pickup_time = models.IntegerField(null=True, blank=True)  # Time from acceptance to pickup
    avg_processing_time = models.IntegerField(null=True, blank=True)  # Time from pickup to ready
    avg_delivery_time = models.IntegerField(null=True, blank=True)  # Time from ready to delivered
    avg_total_time = models.IntegerField(null=True, blank=True)  # Total order fulfillment time

    # Quality metrics
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))]
    )
    rating_count = models.IntegerField(default=0)

    # Issue tracking
    issues_reported = models.IntegerField(default=0)
    items_damaged = models.IntegerField(default=0)
    items_lost = models.IntegerField(default=0)

    # Capacity metrics
    capacity_utilized_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_performance_metrics'
        verbose_name = 'Partner Performance Metric'
        verbose_name_plural = 'Partner Performance Metrics'
        ordering = ['-date', 'partner']
        unique_together = [['partner', 'date']]
        indexes = [
            models.Index(fields=['partner', '-date']),
            models.Index(fields=['-date']),
            models.Index(fields=['partner', 'avg_rating']),
        ]

    def __str__(self):
        return f"{self.partner.business_name} - {self.date}"

    @property
    def acceptance_rate(self):
        """Percentage of orders accepted."""
        if self.orders_received == 0:
            return 0
        return (self.orders_accepted / self.orders_received) * 100

    @property
    def completion_rate(self):
        """Percentage of accepted orders completed."""
        if self.orders_accepted == 0:
            return 0
        return (self.orders_completed / self.orders_accepted) * 100

    @property
    def rejection_rate(self):
        """Percentage of orders rejected."""
        if self.orders_received == 0:
            return 0
        return (self.orders_rejected / self.orders_received) * 100


class CustomerAnalytics(models.Model):
    """
    Customer behavior and value metrics.

    Tracks customer lifetime value, frequency, and engagement.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='analytics'
    )

    # Order metrics
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)

    # Revenue metrics
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    lifetime_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Engagement metrics
    first_order_date = models.DateTimeField(null=True, blank=True)
    last_order_date = models.DateTimeField(null=True, blank=True)
    days_since_last_order = models.IntegerField(null=True, blank=True)
    order_frequency_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )  # Average days between orders

    # Segmentation
    customer_segment = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New Customer'),
            ('occasional', 'Occasional Customer'),
            ('regular', 'Regular Customer'),
            ('vip', 'VIP Customer'),
            ('churned', 'Churned Customer'),
        ],
        default='new'
    )

    # Preferences
    favorite_service_category = models.CharField(max_length=50, blank=True)
    preferred_payment_method = models.CharField(max_length=20, blank=True)

    # Rating given by customer
    avg_rating_given = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))]
    )

    # Churn prediction
    churn_risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )  # 0-100 scale
    is_at_churn_risk = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_analytics'
        verbose_name = 'Customer Analytics'
        verbose_name_plural = 'Customer Analytics'
        ordering = ['-lifetime_value']
        indexes = [
            models.Index(fields=['-lifetime_value']),
            models.Index(fields=['customer_segment']),
            models.Index(fields=['-last_order_date']),
            models.Index(fields=['is_at_churn_risk']),
        ]

    def __str__(self):
        return f"{self.user.email} - LTV: ${self.lifetime_value}"

    def update_metrics(self):
        """Recalculate all metrics from orders."""
        from apps.orders.models import Order

        orders = Order.objects.filter(user=self.user)
        completed = orders.filter(status='delivered')

        self.total_orders = orders.count()
        self.completed_orders = completed.count()
        self.cancelled_orders = orders.filter(status='cancelled').count()

        if completed.exists():
            self.total_spent = sum(order.total_amount for order in completed)
            self.average_order_value = self.total_spent / self.completed_orders
            self.lifetime_value = self.total_spent

            self.first_order_date = completed.order_by('created_at').first().created_at
            self.last_order_date = completed.order_by('-created_at').first().created_at

            # Calculate days since last order
            self.days_since_last_order = (timezone.now() - self.last_order_date).days

            # Calculate order frequency
            if self.completed_orders > 1:
                days_active = (self.last_order_date - self.first_order_date).days
                self.order_frequency_days = days_active / (self.completed_orders - 1)

            # Update segment
            self._update_segment()

            # Update churn risk
            self._calculate_churn_risk()

        self.save()

    def _update_segment(self):
        """Update customer segment based on behavior."""
        if self.completed_orders == 0:
            self.customer_segment = 'new'
        elif self.days_since_last_order and self.days_since_last_order > 90:
            self.customer_segment = 'churned'
        elif self.completed_orders >= 20 or self.lifetime_value >= 1000:
            self.customer_segment = 'vip'
        elif self.completed_orders >= 5:
            self.customer_segment = 'regular'
        else:
            self.customer_segment = 'occasional'

    def _calculate_churn_risk(self):
        """Calculate churn risk score (0-100)."""
        risk_score = 0

        # Days since last order (max 50 points)
        if self.days_since_last_order:
            if self.days_since_last_order > 60:
                risk_score += 50
            elif self.days_since_last_order > 30:
                risk_score += 30
            elif self.days_since_last_order > 14:
                risk_score += 15

        # Low order frequency (max 25 points)
        if self.order_frequency_days and self.order_frequency_days > 30:
            risk_score += 25
        elif self.order_frequency_days and self.order_frequency_days > 14:
            risk_score += 15

        # Low rating (max 25 points)
        if self.avg_rating_given and self.avg_rating_given < 3:
            risk_score += 25
        elif self.avg_rating_given and self.avg_rating_given < 4:
            risk_score += 15

        self.churn_risk_score = min(risk_score, 100)
        self.is_at_churn_risk = self.churn_risk_score >= 50


class ReportSchedule(models.Model):
    """
    Scheduled report generation and delivery.

    Allows scheduling of reports to be generated and emailed.
    """

    REPORT_TYPE_CHOICES = [
        ('revenue', 'Revenue Report'),
        ('orders', 'Orders Report'),
        ('partners', 'Partner Performance Report'),
        ('customers', 'Customer Analytics Report'),
        ('inventory', 'Inventory Report'),
        ('custom', 'Custom Report'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Report configuration
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)

    # Schedule
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)]
    )  # 0=Monday, 6=Sunday (for weekly reports)
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )  # For monthly reports
    time_of_day = models.TimeField(default='09:00:00')

    # Delivery
    email_to = models.JSONField(default=list)  # List of email addresses
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')

    # Filters (JSON for flexibility)
    filters = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    # Created by
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_schedules'
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'next_run_at']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class AnalyticsCache(models.Model):
    """
    Cache for expensive analytics calculations.

    Stores pre-calculated metrics to improve performance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    cache_type = models.CharField(
        max_length=50,
        choices=[
            ('dashboard', 'Dashboard Metrics'),
            ('revenue', 'Revenue Analytics'),
            ('orders', 'Order Analytics'),
            ('partners', 'Partner Analytics'),
            ('customers', 'Customer Analytics'),
        ]
    )

    data = models.JSONField()  # Cached data

    # Cache expiry
    expires_at = models.DateTimeField(db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_cache'
        verbose_name = 'Analytics Cache'
        verbose_name_plural = 'Analytics Cache'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cache_key', 'expires_at']),
            models.Index(fields=['cache_type', 'expires_at']),
        ]

    def __str__(self):
        return f"{self.cache_key} (expires: {self.expires_at})"

    @property
    def is_expired(self):
        """Check if cache has expired."""
        return timezone.now() > self.expires_at

    @classmethod
    def get_cached(cls, key):
        """Get cached data if not expired."""
        try:
            cache = cls.objects.get(cache_key=key)
            if not cache.is_expired:
                return cache.data
            cache.delete()
        except cls.DoesNotExist:
            pass
        return None

    @classmethod
    def set_cached(cls, key, data, cache_type, ttl_minutes=5):
        """Set cached data with TTL."""
        expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        cache, created = cls.objects.update_or_create(
            cache_key=key,
            defaults={
                'data': data,
                'cache_type': cache_type,
                'expires_at': expires_at
            }
        )
        return cache
