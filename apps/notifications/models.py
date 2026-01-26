"""
Notification models for LaundryConnect platform.
"""
import uuid
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    In-app notification model.
    Stores notifications for users about orders, payments, and system events.
    """

    NOTIFICATION_TYPES = [
        # Order notifications
        ('order_created', 'Order Created'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_picked_up', 'Order Picked Up'),
        ('order_in_progress', 'Order In Progress'),
        ('order_ready', 'Order Ready for Delivery'),
        ('order_out_for_delivery', 'Order Out for Delivery'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),

        # Payment notifications
        ('payment_initiated', 'Payment Initiated'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('payment_refunded', 'Payment Refunded'),

        # Refund notifications
        ('refund_requested', 'Refund Requested'),
        ('refund_processing', 'Refund Processing'),
        ('refund_completed', 'Refund Completed'),
        ('refund_failed', 'Refund Failed'),

        # Partner notifications
        ('partner_assigned', 'Partner Assigned to Order'),
        ('partner_approved', 'Partner Account Approved'),
        ('new_order_assigned', 'New Order Assigned'),

        # Account notifications
        ('welcome', 'Welcome to LaundryConnect'),
        ('account_verified', 'Account Verified'),
        ('password_changed', 'Password Changed'),

        # General
        ('general', 'General Notification'),
        ('promotion', 'Promotional Notification'),
    ]

    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    notification_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        help_text='Auto-generated notification ID'
    )

    # User and type
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        db_index=True
    )

    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Related objects (optional)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Status tracking
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether the notification has been read'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the notification was marked as read'
    )

    # Email delivery tracking
    email_sent = models.BooleanField(
        default=False,
        help_text='Whether email notification was sent'
    )
    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the email was sent'
    )
    email_error = models.TextField(
        blank=True,
        help_text='Email sending error message if any'
    )

    # Action and metadata
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='Deep link or action URL for the notification'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata for the notification'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'type', '-created_at']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.notification_id} - {self.title}"

    def save(self, *args, **kwargs):
        """Generate notification_id if not set."""
        if not self.notification_id:
            self.notification_id = self._generate_notification_id()
        super().save(*args, **kwargs)

    def _generate_notification_id(self):
        """Generate unique notification ID in format: NOTIF{YYYYMMDD}{8-char}"""
        date_str = datetime.now().strftime('%Y%m%d')
        unique_str = str(uuid.uuid4())[:8].upper()
        return f"NOTIF{date_str}{unique_str}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])


class NotificationTemplate(models.Model):
    """
    Email and notification templates for different event types.
    """

    # Same types as Notification.NOTIFICATION_TYPES
    type = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Notification type this template is for'
    )
    name = models.CharField(
        max_length=255,
        help_text='Human-readable template name'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of when this template is used'
    )

    # Email template
    email_subject = models.CharField(
        max_length=255,
        help_text='Email subject line. Can use {{ variables }}'
    )
    email_body_html = models.TextField(
        help_text='HTML email body. Can use {{ variables }}'
    )
    email_body_text = models.TextField(
        help_text='Plain text email body. Can use {{ variables }}'
    )

    # In-app notification template
    title_template = models.CharField(
        max_length=255,
        help_text='Notification title template. Can use {{ variables }}'
    )
    message_template = models.TextField(
        help_text='Notification message template. Can use {{ variables }}'
    )

    # SMS template (for future use)
    sms_template = models.CharField(
        max_length=160,
        blank=True,
        help_text='SMS message template (max 160 chars). Can use {{ variables }}'
    )

    # Action configuration
    action_url_template = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL template for notification action. Can use {{ variables }}'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this template is currently in use'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['type']
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'

    def __str__(self):
        return f"{self.name} ({self.type})"


class NotificationPreference(models.Model):
    """
    User notification preferences.
    Controls which types of notifications a user wants to receive and through which channels.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        primary_key=True
    )

    # Order notifications
    order_updates_email = models.BooleanField(
        default=True,
        help_text='Receive order status updates via email'
    )
    order_updates_push = models.BooleanField(
        default=True,
        help_text='Receive order status updates as push notifications'
    )

    # Payment notifications
    payment_updates_email = models.BooleanField(
        default=True,
        help_text='Receive payment confirmations via email'
    )
    payment_updates_push = models.BooleanField(
        default=True,
        help_text='Receive payment updates as push notifications'
    )

    # Refund notifications
    refund_updates_email = models.BooleanField(
        default=True,
        help_text='Receive refund updates via email'
    )
    refund_updates_push = models.BooleanField(
        default=True,
        help_text='Receive refund updates as push notifications'
    )

    # Partner notifications (for partner users)
    partner_updates_email = models.BooleanField(
        default=True,
        help_text='Receive partner-related updates via email'
    )
    partner_updates_push = models.BooleanField(
        default=True,
        help_text='Receive partner updates as push notifications'
    )

    # Marketing and promotions
    marketing_emails = models.BooleanField(
        default=False,
        help_text='Receive marketing and promotional emails'
    )
    promotional_push = models.BooleanField(
        default=False,
        help_text='Receive promotional push notifications'
    )

    # Account notifications
    account_updates_email = models.BooleanField(
        default=True,
        help_text='Receive account-related updates via email'
    )

    # SMS preferences (for future)
    order_updates_sms = models.BooleanField(
        default=False,
        help_text='Receive order updates via SMS'
    )
    payment_updates_sms = models.BooleanField(
        default=False,
        help_text='Receive payment updates via SMS'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.email}"

    def should_send_email(self, notification_type):
        """Check if email should be sent for given notification type."""
        type_mapping = {
            'order': self.order_updates_email,
            'payment': self.payment_updates_email,
            'refund': self.refund_updates_email,
            'partner': self.partner_updates_email,
            'account': self.account_updates_email,
            'promotion': self.marketing_emails,
        }

        # Extract category from notification type (e.g., 'order_created' -> 'order')
        category = notification_type.split('_')[0]
        return type_mapping.get(category, True)

    def should_send_push(self, notification_type):
        """Check if push notification should be sent for given notification type."""
        type_mapping = {
            'order': self.order_updates_push,
            'payment': self.payment_updates_push,
            'refund': self.refund_updates_push,
            'partner': self.partner_updates_push,
            'promotion': self.promotional_push,
        }

        category = notification_type.split('_')[0]
        return type_mapping.get(category, True)


class PushSubscription(models.Model):
    """
    Browser push notification subscription.
    Stores push subscription information for sending Web Push notifications.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        db_index=True,
        help_text='User who owns this push subscription'
    )

    # Push subscription details (from browser's PushSubscription object)
    endpoint = models.URLField(
        max_length=500,
        help_text='Push service endpoint URL'
    )
    p256dh_key = models.CharField(
        max_length=255,
        help_text='P256DH public key for encryption'
    )
    auth_key = models.CharField(
        max_length=255,
        help_text='Auth secret for encryption'
    )

    # Device information
    device_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Device/browser name (e.g., "Chrome on MacBook")'
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text='Browser user agent string'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether this subscription is active'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time a push was sent to this subscription'
    )

    class Meta:
        db_table = 'push_subscriptions'
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'
        ordering = ['-created_at']
        unique_together = [['user', 'endpoint']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['endpoint']),
        ]

    def __str__(self):
        device = self.device_name or 'Unknown Device'
        return f"{self.user.email} - {device}"

    def get_subscription_info(self):
        """
        Get subscription info in format required by pywebpush.

        Returns:
            dict: Subscription info with endpoint and keys
        """
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh_key,
                'auth': self.auth_key
            }
        }
