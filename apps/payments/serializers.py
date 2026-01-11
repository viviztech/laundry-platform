"""
Serializers for payments app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import Payment, Wallet, WalletTransaction, Refund, PaymentMethod

User = get_user_model()


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""

    # For mobile app compatibility - map card_last4 to last4
    last4 = serializers.CharField(source='card_last4', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'type', 'provider', 'nickname', 'is_default',
            'is_active', 'card_last4', 'last4', 'card_brand',
            'card_expiry_month', 'card_expiry_year', 'upi_id',
            'bank_name', 'wallet_provider', 'wallet_number',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate payment method data."""
        method_type = data.get('type')

        if method_type == 'card':
            if not data.get('card_last4') or not data.get('card_brand'):
                raise serializers.ValidationError(
                    "Card details (card_last4, card_brand) are required for card payment method."
                )
        elif method_type == 'upi':
            if not data.get('upi_id'):
                raise serializers.ValidationError(
                    "UPI ID is required for UPI payment method."
                )
        elif method_type == 'netbanking':
            if not data.get('bank_name'):
                raise serializers.ValidationError(
                    "Bank name is required for net banking payment method."
                )
        elif method_type == 'wallet':
            if not data.get('wallet_provider'):
                raise serializers.ValidationError(
                    "Wallet provider is required for wallet payment method."
                )

        return data


class PaymentMethodCreateSerializer(serializers.Serializer):
    """Serializer for creating a new payment method."""

    type = serializers.ChoiceField(choices=PaymentMethod.TYPE_CHOICES)
    provider = serializers.CharField(max_length=100, required=False, allow_blank=True)
    nickname = serializers.CharField(max_length=100, required=False, allow_blank=True)
    is_default = serializers.BooleanField(default=False)

    # Card details
    card_number = serializers.CharField(max_length=19, required=False, allow_blank=True, write_only=True)
    card_holder = serializers.CharField(max_length=100, required=False, allow_blank=True, write_only=True)
    card_token = serializers.CharField(required=False, allow_blank=True)
    card_last4 = serializers.CharField(max_length=4, required=False, allow_blank=True)
    card_brand = serializers.CharField(max_length=50, required=False, allow_blank=True)
    card_expiry_month = serializers.IntegerField(required=False, allow_null=True)
    card_expiry_year = serializers.IntegerField(required=False, allow_null=True)
    cvv = serializers.CharField(max_length=4, required=False, allow_blank=True, write_only=True)

    # UPI details
    upi_id = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # Net Banking details
    bank_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # Wallet details
    wallet_provider = serializers.CharField(max_length=50, required=False, allow_blank=True)
    wallet_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate(self, data):
        """Validate payment method creation data."""
        method_type = data.get('type')

        if method_type == 'card':
            # For card payments, require either token or card details for tokenization
            if not data.get('card_number') and not data.get('card_token'):
                raise serializers.ValidationError(
                    "Card number is required for card payment method."
                )
            # Extract last 4 digits if card number provided
            if data.get('card_number'):
                data['card_last4'] = data['card_number'][-4:]
                # Set provider as card brand if not provided
                if not data.get('provider'):
                    data['provider'] = data.get('card_brand', 'Card')
        elif method_type == 'upi':
            if not data.get('upi_id'):
                raise serializers.ValidationError(
                    "UPI ID is required for UPI payment method."
                )
            # Extract provider from UPI ID
            if not data.get('provider') and '@' in data['upi_id']:
                data['provider'] = data['upi_id'].split('@')[1].capitalize()
        elif method_type == 'netbanking':
            if not data.get('bank_name'):
                raise serializers.ValidationError(
                    "Bank name is required for net banking payment method."
                )
            if not data.get('provider'):
                data['provider'] = data['bank_name']
        elif method_type == 'wallet':
            if not data.get('wallet_provider'):
                raise serializers.ValidationError(
                    "Wallet provider is required for wallet payment method."
                )
            if not data.get('provider'):
                data['provider'] = data['wallet_provider']

        return data


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for WalletTransaction model."""

    # Mobile app compatibility - map transaction_type to type and add status
    type = serializers.CharField(source='transaction_type', read_only=True)
    status = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(source='order.id', read_only=True, allow_null=True)

    class Meta:
        model = WalletTransaction
        fields = (
            'id', 'transaction_id', 'transaction_type', 'type', 'amount',
            'balance_after', 'description', 'payment', 'order', 'order_id',
            'refund', 'status', 'created_at'
        )
        read_only_fields = (
            'id', 'transaction_id', 'balance_after', 'created_at'
        )

    def get_status(self, obj):
        """Get transaction status - always completed for wallet transactions."""
        return 'completed'


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()  # Mobile app compatibility
    cashback = serializers.SerializerMethodField()  # Placeholder for future feature
    rewards = serializers.SerializerMethodField()  # Placeholder for future feature

    class Meta:
        model = Wallet
        fields = (
            'id', 'user', 'user_email', 'balance', 'currency',
            'cashback', 'rewards', 'is_active', 'is_locked',
            'recent_transactions', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'balance', 'is_locked',
            'created_at', 'updated_at'
        )

    def get_recent_transactions(self, obj):
        """Get recent wallet transactions."""
        transactions = obj.transactions.all()[:5]
        return WalletTransactionSerializer(transactions, many=True).data

    def get_currency(self, obj):
        """Get currency - default to INR."""
        return 'INR'

    def get_cashback(self, obj):
        """Get cashback balance - placeholder for future feature."""
        return 0.00

    def get_rewards(self, obj):
        """Get rewards balance - placeholder for future feature."""
        return 0.00


class WalletAddBalanceSerializer(serializers.Serializer):
    """Serializer for adding balance to wallet."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    order_id_display = serializers.CharField(source='order.order_id', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'payment_id', 'order', 'order_id_display',
            'user', 'user_email', 'amount', 'transaction_fee',
            'net_amount', 'currency', 'method', 'method_display',
            'gateway', 'gateway_payment_id', 'gateway_order_id',
            'gateway_signature', 'status', 'failure_reason',
            'error_message', 'metadata', 'completed_at',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'payment_id', 'user', 'net_amount',
            'gateway_payment_id', 'gateway_order_id',
            'gateway_signature', 'completed_at',
            'created_at', 'updated_at'
        )


class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing payments."""

    order_id_display = serializers.CharField(source='order.order_id', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'payment_id', 'order_id_display', 'amount',
            'method', 'method_display', 'gateway',
            'status', 'created_at', 'completed_at'
        )


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating a payment."""

    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    payment_method_id = serializers.UUIDField(required=False, allow_null=True)
    gateway = serializers.ChoiceField(choices=Payment.GATEWAY_CHOICES, default='razorpay')

    def validate_payment_method_id(self, value):
        """Validate saved payment method belongs to user."""
        if value:
            user = self.context.get('request').user
            if not PaymentMethod.objects.filter(id=value, user=user, is_active=True).exists():
                raise serializers.ValidationError("Invalid payment method.")
        return value


class VerifyPaymentSerializer(serializers.Serializer):
    """Serializer for verifying a payment."""

    gateway_payment_id = serializers.CharField(max_length=255)
    gateway_order_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    gateway_signature = serializers.CharField(max_length=255, required=False, allow_blank=True)


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for Refund model."""

    payment_id_display = serializers.CharField(source='payment.payment_id', read_only=True)
    order_id_display = serializers.CharField(source='order.order_id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    processed_by_email = serializers.EmailField(source='processed_by.email', read_only=True)

    class Meta:
        model = Refund
        fields = (
            'id', 'refund_id', 'payment', 'payment_id_display',
            'order', 'order_id_display', 'user', 'user_email',
            'amount', 'reason', 'description', 'status',
            'processed_by', 'processed_by_email', 'processed_at',
            'completed_at', 'gateway_refund_id', 'error_message',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'refund_id', 'user', 'processed_by',
            'processed_at', 'completed_at', 'gateway_refund_id',
            'created_at', 'updated_at'
        )


class RefundListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing refunds."""

    payment_id_display = serializers.CharField(source='payment.payment_id', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Refund
        fields = (
            'id', 'refund_id', 'payment_id_display', 'amount',
            'reason', 'reason_display', 'status',
            'status_display', 'created_at'
        )


class CreateRefundSerializer(serializers.Serializer):
    """Serializer for creating a refund request."""

    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    reason = serializers.ChoiceField(choices=Refund.REASON_CHOICES)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, data):
        """Validate refund request."""
        try:
            payment = Payment.objects.get(id=data['payment_id'])
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Invalid payment ID.")

        # Validate payment status
        if payment.status != 'completed':
            raise serializers.ValidationError(
                "Can only refund completed payments."
            )

        # Validate amount
        amount = data.get('amount')
        if amount:
            if amount > payment.amount:
                raise serializers.ValidationError(
                    "Refund amount cannot exceed payment amount."
                )
            if amount <= 0:
                raise serializers.ValidationError(
                    "Refund amount must be greater than 0."
                )
        else:
            # Full refund
            data['amount'] = payment.amount

        # Check for existing refunds
        total_refunded = Refund.objects.filter(
            payment=payment,
            status__in=['pending', 'processing', 'completed']
        ).aggregate(total=serializers.models.Sum('amount'))['total'] or Decimal('0.00')

        if total_refunded + data['amount'] > payment.amount:
            raise serializers.ValidationError(
                f"Total refund amount cannot exceed payment amount. "
                f"Already refunded: {total_refunded}"
            )

        return data


class ProcessRefundSerializer(serializers.Serializer):
    """Serializer for processing a refund."""

    status = serializers.ChoiceField(choices=['processing', 'completed', 'failed'])
    gateway_refund_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    error_message = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, data):
        """Validate refund processing data."""
        if data['status'] == 'failed' and not data.get('error_message'):
            raise serializers.ValidationError(
                "Error message is required when marking refund as failed."
            )
        return data
