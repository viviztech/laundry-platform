"""
Order management models for LaundryConnect platform.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal


class Order(models.Model):
    """Main order model for laundry bookings."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('wallet', 'Wallet'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, db_index=True)

    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    # Address information
    pickup_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.PROTECT,
        related_name='pickup_orders'
    )
    delivery_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.PROTECT,
        related_name='delivery_orders',
        null=True,
        blank=True
    )

    # Order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Payment
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    payment_id = models.CharField(max_length=255, blank=True)

    # Schedule
    pickup_date = models.DateField()
    pickup_time_slot = models.CharField(max_length=50)  # e.g., "09:00-12:00"
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time_slot = models.CharField(max_length=50, blank=True)

    # Additional information
    special_instructions = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)  # For staff use

    # Partner assignment
    assigned_partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders'
    )
    partner_accepted_at = models.DateTimeField(null=True, blank=True)
    partner_rejected_at = models.DateTimeField(null=True, blank=True)
    partner_rejection_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['pickup_date']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        """Generate order number if not exists."""
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"LC{date_str}{random_str}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculate and update total amount."""
        self.total_amount = (
            self.subtotal +
            self.tax_amount +
            self.delivery_fee -
            self.discount_amount
        )


class OrderItem(models.Model):
    """Individual items in an order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    # Item details
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.service.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate total price based on quantity and unit price."""
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class OrderAddon(models.Model):
    """Add-ons applied to order items or entire order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='addons'
    )
    addon = models.ForeignKey(
        'services.Addon',
        on_delete=models.PROTECT,
        related_name='order_addons'
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='addons',
        null=True,
        blank=True
    )

    # Pricing
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_addons'
        verbose_name = 'Order Add-on'
        verbose_name_plural = 'Order Add-ons'

    def __str__(self):
        return f"{self.addon.name} for Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        """Calculate total price."""
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track status changes for orders."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    # Status change
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)

    # Change details
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes'
    )
    notes = models.TextField(blank=True)

    # Timestamp
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"


class OrderRating(models.Model):
    """Customer ratings and reviews for completed orders."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_ratings'
    )

    # Rating
    service_rating = models.IntegerField(
        validators=[MinValueValidator(1), MinValueValidator(5)]
    )
    delivery_rating = models.IntegerField(
        validators=[MinValueValidator(1), MinValueValidator(5)]
    )
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MinValueValidator(5)]
    )

    # Review
    review = models.TextField(blank=True)

    # Metadata
    is_published = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_ratings'
        verbose_name = 'Order Rating'
        verbose_name_plural = 'Order Ratings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Rating for {self.order.order_number} - {self.overall_rating}/5"
