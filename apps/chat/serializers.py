"""
Serializers for Chat API endpoints.
"""

from rest_framework import serializers
from django.db import transaction

from .models import ChatRoom, ChatMessage, TypingIndicator
from apps.accounts.models import User
from apps.orders.models import Order
from apps.partners.models import Partner


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""

    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    room_id = serializers.CharField(source='room.room_id', read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'room',
            'room_id',
            'sender',
            'sender_name',
            'sender_email',
            'message_type',
            'content',
            'file',
            'file_url',
            'metadata',
            'is_read',
            'read_at',
            'is_delivered',
            'delivered_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'sender',
            'is_read',
            'read_at',
            'is_delivered',
            'delivered_at',
            'created_at',
            'updated_at',
        ]

    def get_sender_name(self, obj):
        """Get sender's full name or email."""
        return obj.sender.get_full_name() or obj.sender.email

    def get_file_url(self, obj):
        """Get full URL for uploaded file."""
        return obj.get_file_url()

    def validate(self, data):
        """Validate message data."""
        message_type = data.get('message_type', 'text')
        content = data.get('content', '')
        file_obj = data.get('file')

        # Text messages must have content
        if message_type == 'text' and not content.strip():
            raise serializers.ValidationError({
                'content': 'Text messages must have content.'
            })

        # Image/file messages must have file
        if message_type in ['image', 'file'] and not file_obj:
            raise serializers.ValidationError({
                'file': f'{message_type.capitalize()} messages must include a file.'
            })

        # Location messages must have metadata with coordinates
        if message_type == 'location':
            metadata = data.get('metadata', {})
            if not metadata.get('latitude') or not metadata.get('longitude'):
                raise serializers.ValidationError({
                    'metadata': 'Location messages must include latitude and longitude.'
                })

        return data


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages."""

    class Meta:
        model = ChatMessage
        fields = [
            'room',
            'message_type',
            'content',
            'file',
            'metadata',
        ]

    def create(self, validated_data):
        """Create message with sender from request user."""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""

    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    partner_name = serializers.CharField(source='partner.business_name', read_only=True)
    partner_email = serializers.EmailField(source='partner.user.email', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'room_id',
            'order',
            'order_number',
            'order_status',
            'customer',
            'customer_name',
            'customer_email',
            'partner',
            'partner_name',
            'partner_email',
            'is_active',
            'last_message_at',
            'last_message',
            'customer_unread_count',
            'partner_unread_count',
            'unread_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'room_id',
            'customer',
            'partner',
            'last_message_at',
            'customer_unread_count',
            'partner_unread_count',
            'created_at',
            'updated_at',
        ]

    def get_last_message(self, obj):
        """Get the last message in this room."""
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'sender_name': last_msg.sender.get_full_name() or last_msg.sender.email,
                'message_type': last_msg.message_type,
                'content': last_msg.content[:100],  # Truncate long messages
                'created_at': last_msg.created_at,
            }
        return None

    def get_unread_count(self, obj):
        """Get unread count for current user."""
        request = self.context.get('request')
        if not request or not request.user:
            return 0

        if request.user == obj.customer:
            return obj.customer_unread_count
        elif hasattr(obj.partner, 'user') and request.user == obj.partner.user:
            return obj.partner_unread_count
        return 0


class ChatRoomCreateSerializer(serializers.Serializer):
    """Serializer for creating a chat room for an order."""

    order_id = serializers.UUIDField()

    def validate_order_id(self, value):
        """Validate that order exists and belongs to user."""
        request = self.context.get('request')
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

        # Check if user is customer or partner
        is_customer = order.customer == request.user
        is_partner = (
            hasattr(order, 'assigned_partner') and
            order.assigned_partner and
            order.assigned_partner.user == request.user
        )

        if not (is_customer or is_partner):
            raise serializers.ValidationError(
                "You don't have permission to create a chat for this order."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create chat room for order."""
        order = Order.objects.get(id=validated_data['order_id'])

        # Check if chat room already exists
        if hasattr(order, 'chat_room'):
            return order.chat_room

        # Ensure order has an assigned partner
        if not order.assigned_partner:
            raise serializers.ValidationError({
                'order_id': 'Order must have an assigned partner to create a chat room.'
            })

        # Create chat room
        chat_room = ChatRoom.objects.create(
            order=order,
            customer=order.customer,
            partner=order.assigned_partner,
        )

        return chat_room


class TypingIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for typing indicators."""

    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TypingIndicator
        fields = [
            'room',
            'user',
            'user_name',
            'user_email',
            'started_at',
        ]
        read_only_fields = ['user', 'started_at']


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read."""

    message_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of message IDs to mark as read. If not provided, all unread messages will be marked."
    )

    def validate_message_ids(self, value):
        """Validate that messages exist and belong to the room."""
        if not value:
            return value

        room_id = self.context.get('room_id')
        messages = ChatMessage.objects.filter(
            id__in=value,
            room__room_id=room_id
        )

        if messages.count() != len(value):
            raise serializers.ValidationError(
                "Some message IDs are invalid or don't belong to this room."
            )

        return value
