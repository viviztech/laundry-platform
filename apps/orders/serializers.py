"""
Serializers for orders app.
"""

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, OrderAddon, OrderStatusHistory, OrderRating
from apps.services.serializers import ServiceListSerializer, AddonSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""

    service_name = serializers.CharField(source='service.name', read_only=True)
    service_details = ServiceListSerializer(source='service', read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 'service', 'service_name', 'service_details',
            'quantity', 'unit_price', 'total_price', 'notes',
            'created_at'
        )
        read_only_fields = ('id', 'total_price', 'created_at')


class OrderAddonSerializer(serializers.ModelSerializer):
    """Serializer for OrderAddon model."""

    addon_name = serializers.CharField(source='addon.name', read_only=True)
    addon_details = AddonSerializer(source='addon', read_only=True)

    class Meta:
        model = OrderAddon
        fields = (
            'id', 'addon', 'addon_name', 'addon_details',
            'order_item', 'quantity', 'unit_price',
            'total_price', 'created_at'
        )
        read_only_fields = ('id', 'total_price', 'created_at')


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for OrderStatusHistory model."""

    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = (
            'id', 'old_status', 'new_status',
            'changed_by', 'changed_by_email',
            'notes', 'changed_at'
        )
        read_only_fields = ('id', 'changed_at')


class OrderRatingSerializer(serializers.ModelSerializer):
    """Serializer for OrderRating model."""

    class Meta:
        model = OrderRating
        fields = (
            'id', 'order', 'service_rating', 'delivery_rating',
            'overall_rating', 'review', 'is_published',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        """Ensure ratings are between 1 and 5."""
        for field in ['service_rating', 'delivery_rating', 'overall_rating']:
            if field in attrs and (attrs[field] < 1 or attrs[field] > 5):
                raise serializers.ValidationError({
                    field: "Rating must be between 1 and 5."
                })
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """Detailed serializer for Order model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    addons = OrderAddonSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    rating = OrderRatingSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'user_email',
            'pickup_address', 'delivery_address',
            'status', 'payment_status', 'payment_method', 'payment_id',
            'subtotal', 'tax_amount', 'delivery_fee',
            'discount_amount', 'total_amount',
            'pickup_date', 'pickup_time_slot',
            'delivery_date', 'delivery_time_slot',
            'special_instructions', 'customer_notes',
            'items', 'addons', 'status_history', 'rating',
            'created_at', 'updated_at', 'confirmed_at', 'completed_at'
        )
        read_only_fields = (
            'id', 'order_number', 'user', 'created_at', 'updated_at',
            'confirmed_at', 'completed_at'
        )


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing orders."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user_email',
            'status', 'payment_status',
            'total_amount', 'pickup_date',
            'items_count', 'created_at'
        )

    def get_items_count(self, obj):
        """Return the number of items in the order."""
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating a new order."""

    pickup_address = serializers.UUIDField()
    delivery_address = serializers.UUIDField(required=False, allow_null=True)
    pickup_date = serializers.DateField()
    pickup_time_slot = serializers.CharField(max_length=50)
    delivery_date = serializers.DateField(required=False, allow_null=True)
    delivery_time_slot = serializers.CharField(max_length=50, required=False, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)

    # Order items
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    addons = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )

    def validate_pickup_date(self, value):
        """Ensure pickup date is not in the past."""
        if value < timezone.now().date():
            raise serializers.ValidationError("Pickup date cannot be in the past.")
        return value

    def validate_items(self, value):
        """Validate order items structure."""
        for item in value:
            if 'service_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'service_id' and 'quantity'."
                )
            if item['quantity'] < 1:
                raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status."""

    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        """Validate status transition."""
        order = self.context.get('order')
        if not order:
            return value

        # Define valid status transitions
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['picked_up', 'cancelled'],
            'picked_up': ['in_progress', 'cancelled'],
            'in_progress': ['ready'],
            'ready': ['out_for_delivery'],
            'out_for_delivery': ['delivered'],
            'delivered': [],
            'cancelled': [],
        }

        if value not in valid_transitions.get(order.status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {order.status} to {value}."
            )
        return value
