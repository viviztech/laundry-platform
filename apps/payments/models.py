"""
Payment and wallet models for LaundryConnect platform.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):
    """Payment transactions for orders."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('wallet', 'Wallet'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    GATEWAY_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('stripe', 'Stripe'),
        ('paytm', 'Paytm'),
        ('phonepe', 'PhonePe'),
        ('manual', 'Manual'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.CharField(max_length=255, unique=True, db_index=True)

    # Related entities
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, default='razorpay')

    # Gateway details
    gateway_payment_id = models.CharField(max_length=255, blank=True)
    gateway_order_id = models.CharField(max_length=255, blank=True)
    gateway_signature = models.CharField(max_length=500, blank=True)

    # Transaction details
    transaction_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['gateway_payment_id']),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        """Generate payment ID if not exists."""
        if not self.payment_id:
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.payment_id = f"PAY{date_str}{random_str}"

        # Calculate net amount
        self.net_amount = self.amount - self.transaction_fee

        super().save(*args, **kwargs)


class Wallet(models.Model):
    """Digital wallet for users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )

    # Balance
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f"{self.user.email} - Wallet: {self.balance} INR"

    def add_balance(self, amount, description='', transaction_type='credit'):
        """Add balance to wallet."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.balance += Decimal(str(amount))
        self.save()

        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type=transaction_type,
            balance_after=self.balance,
            description=description
        )

    def deduct_balance(self, amount, description='', transaction_type='debit'):
        """Deduct balance from wallet."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if self.balance < Decimal(str(amount)):
            raise ValueError("Insufficient balance")

        self.balance -= Decimal(str(amount))
        self.save()

        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type=transaction_type,
            balance_after=self.balance,
            description=description
        )


class WalletTransaction(models.Model):
    """Wallet transaction history."""

    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
        ('cashback', 'Cashback'),
        ('reward', 'Reward'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True)

    # Related entities
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )

    # Transaction details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed'
    )

    # Balance tracking
    balance_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Description
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} {self.amount}"

    def save(self, *args, **kwargs):
        """Generate transaction ID if not exists."""
        if not self.transaction_id:
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.transaction_id = f"TXN{date_str}{random_str}"
        super().save(*args, **kwargs)


class Refund(models.Model):
    """Refund requests and processing."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    REASON_CHOICES = [
        ('order_cancelled', 'Order Cancelled'),
        ('service_issue', 'Service Issue'),
        ('quality_issue', 'Quality Issue'),
        ('duplicate_payment', 'Duplicate Payment'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_id = models.CharField(max_length=255, unique=True, db_index=True)

    # Related entities
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='refunds'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='refunds'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='refunds'
    )

    # Refund details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True)

    # Gateway details
    gateway_refund_id = models.CharField(max_length=255, blank=True)

    # Processing details
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'refunds'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['refund_id']),
            models.Index(fields=['payment', '-created_at']),
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount}"

    def save(self, *args, **kwargs):
        """Generate refund ID if not exists."""
        if not self.refund_id:
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.refund_id = f"RFD{date_str}{random_str}"
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Saved payment methods for users."""

    TYPE_CHOICES = [
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Digital Wallet'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )

    # Method details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    provider = models.CharField(max_length=100, blank=True)  # Provider name (Visa, HDFC, Paytm, etc.)
    nickname = models.CharField(max_length=100, blank=True)

    # For cards
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # Visa, Mastercard, etc.
    card_expiry_month = models.IntegerField(null=True, blank=True)
    card_expiry_year = models.IntegerField(null=True, blank=True)

    # For UPI
    upi_id = models.CharField(max_length=100, blank=True)

    # For Net Banking
    bank_name = models.CharField(max_length=100, blank=True)

    # For Digital Wallets
    wallet_provider = models.CharField(max_length=50, blank=True)  # Paytm, PhonePe, GPay, etc.
    wallet_number = models.CharField(max_length=20, blank=True)

    # Gateway token
    gateway_token = models.CharField(max_length=255, blank=True)

    # Metadata
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} •••• {self.card_last4}"
        elif self.type == 'upi':
            return f"UPI: {self.upi_id}"
        elif self.type == 'netbanking':
            return f"Net Banking: {self.bank_name}"
        elif self.type == 'wallet':
            return f"{self.wallet_provider} Wallet"
        return f"{self.type} - {self.nickname}"

    def save(self, *args, **kwargs):
        """Ensure only one default payment method per user."""
        if self.is_default:
            # Set all other payment methods for this user to non-default
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
