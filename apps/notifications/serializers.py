"""
Serializers for notifications app.
"""
from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    order_number = serializers.CharField(
        source='order.order_number',
        read_only=True,
        allow_null=True
    )
    payment_id = serializers.CharField(
        source='payment.payment_id',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Notification
        fields = (
            'id', 'notification_id', 'user', 'user_email',
            'type', 'type_display', 'title', 'message',
            'order', 'order_number', 'payment', 'payment_id',
            'is_read', 'read_at', 'email_sent', 'email_sent_at',
            'action_url', 'metadata', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'notification_id', 'user', 'read_at', 'email_sent',
            'email_sent_at', 'created_at', 'updated_at'
        )


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists."""

    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'notification_id', 'type', 'type_display',
            'title', 'is_read', 'created_at'
        )


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""

    class Meta:
        model = NotificationTemplate
        fields = (
            'id', 'type', 'name', 'description',
            'email_subject', 'email_body_html', 'email_body_text',
            'title_template', 'message_template', 'sms_template',
            'action_url_template', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = NotificationPreference
        fields = (
            'user', 'user_email',
            'order_updates_email', 'order_updates_push',
            'payment_updates_email', 'payment_updates_push',
            'refund_updates_email', 'refund_updates_push',
            'partner_updates_email', 'partner_updates_push',
            'marketing_emails', 'promotional_push',
            'account_updates_email',
            'order_updates_sms', 'payment_updates_sms',
            'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'created_at', 'updated_at')


class MarkNotificationReadSerializer(serializers.Serializer):
    """Serializer for marking notification as read."""

    is_read = serializers.BooleanField(default=True)


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for creating bulk notifications."""

    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text='List of user IDs to send notifications to'
    )
    notification_type = serializers.CharField(
        max_length=50,
        help_text='Type of notification to send'
    )
    context_data = serializers.JSONField(
        required=False,
        help_text='Optional context data for notification'
    )


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for push subscriptions."""

    class Meta:
        model = PushSubscription
        fields = ['id', 'endpoint', 'p256dh_key', 'auth_key', 'device_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PushSubscriptionInputSerializer(serializers.Serializer):
    """Serializer for browser push subscription input."""

    endpoint = serializers.URLField(required=True)
    keys = serializers.DictField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, max_length=100)

    def validate_keys(self, value):
        """Validate keys contain required fields."""
        if 'p256dh' not in value or 'auth' not in value:
            raise serializers.ValidationError("Keys must contain 'p256dh' and 'auth' fields")
        return value

    def create(self, validated_data):
        """Create push subscription from browser subscription object."""
        user = self.context['request'].user
        endpoint = validated_data['endpoint']
        keys = validated_data['keys']

        subscription, created = PushSubscription.objects.update_or_create(
            user=user,
            endpoint=endpoint,
            defaults={
                'p256dh_key': keys['p256dh'],
                'auth_key': keys['auth'],
                'device_name': validated_data.get('device_name', ''),
                'user_agent': self.context['request'].META.get('HTTP_USER_AGENT', ''),
                'is_active': True
            }
        )
        return subscription
