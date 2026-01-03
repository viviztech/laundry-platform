"""
Signal handlers for notification system.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.orders.models import Order, OrderStatusHistory
from apps.payments.models import Payment, Refund
from apps.partners.models import Partner
from .models import Notification, NotificationPreference
from .utils import create_notification
from .tasks import send_notification_email, send_notification_sms, send_push_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance, created, **kwargs):
    """
    Create notification when order is created or status changes.
    """
    if created:
        # New order created
        create_notification(
            user=instance.user,
            notification_type='order_created',
            order=instance,
        )
    else:
        # Check if status changed
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # Status changed, create appropriate notification
                notification_type = f'order_{instance.status}'
                create_notification(
                    user=instance.user,
                    notification_type=notification_type,
                    order=instance,
                )
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Payment)
def payment_status_changed(sender, instance, created, **kwargs):
    """
    Create notification when payment status changes.
    """
    if created and instance.status == 'pending':
        create_notification(
            user=instance.user,
            notification_type='payment_initiated',
            payment=instance,
        )
    elif instance.status == 'completed':
        create_notification(
            user=instance.user,
            notification_type='payment_completed',
            payment=instance,
        )
    elif instance.status == 'failed':
        create_notification(
            user=instance.user,
            notification_type='payment_failed',
            payment=instance,
        )
    elif instance.status == 'refunded':
        create_notification(
            user=instance.user,
            notification_type='payment_refunded',
            payment=instance,
        )


@receiver(post_save, sender=Refund)
def refund_status_changed(sender, instance, created, **kwargs):
    """
    Create notification when refund is requested or status changes.
    """
    if created:
        create_notification(
            user=instance.user,
            notification_type='refund_requested',
            payment=instance.payment,
        )
    elif instance.status == 'processing':
        create_notification(
            user=instance.user,
            notification_type='refund_processing',
            payment=instance.payment,
        )
    elif instance.status == 'completed':
        create_notification(
            user=instance.user,
            notification_type='refund_completed',
            payment=instance.payment,
        )
    elif instance.status == 'failed':
        create_notification(
            user=instance.user,
            notification_type='refund_failed',
            payment=instance.payment,
        )


@receiver(post_save, sender=Partner)
def partner_status_changed(sender, instance, created, **kwargs):
    """
    Create notification when partner is approved.
    """
    if not created:
        try:
            old_partner = Partner.objects.get(pk=instance.pk)
            if not old_partner.is_verified and instance.is_verified:
                # Partner just got verified
                create_notification(
                    user=instance.user,
                    notification_type='partner_approved',
                )
        except Partner.DoesNotExist:
            pass


# Create default notification preferences for new users
@receiver(post_save, sender='accounts.User')
def create_notification_preferences(sender, instance, created, **kwargs):
    """
    Create default notification preferences for new users.
    """
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


# ===== WebSocket Broadcasting =====

@receiver(post_save, sender=Notification)
def broadcast_notification_created(sender, instance, created, **kwargs):
    """
    Broadcast notification to user's WebSocket when created.
    Also triggers email and SMS sending via Celery.
    """
    if created:
        # Send email asynchronously
        send_notification_email.delay(str(instance.id))

        # Send SMS asynchronously (if configured and user has opted in)
        send_notification_sms.delay(str(instance.id))

        # Send push notification asynchronously (if user has active subscriptions)
        send_push_notification.delay(str(instance.id))

        # Broadcast to WebSocket
        try:
            channel_layer = get_channel_layer()
            notification_data = {
                'id': str(instance.id),
                'notification_id': instance.notification_id,
                'type': instance.type,
                'title': instance.title,
                'message': instance.message,
                'is_read': instance.is_read,
                'action_url': instance.action_url,
                'created_at': instance.created_at.isoformat(),
                'order_id': str(instance.order.id) if instance.order else None,
                'payment_id': str(instance.payment.id) if instance.payment else None,
            }

            # Send to user's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.user.id}',
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )

            logger.info(f"Broadcasted notification {instance.notification_id} to user {instance.user.id}")

        except Exception as e:
            logger.error(f"Error broadcasting notification: {str(e)}")


@receiver(post_save, sender=Order)
def broadcast_order_update(sender, instance, created, **kwargs):
    """
    Broadcast order updates to WebSocket channel for real-time tracking.
    """
    if not created:  # Only for updates, not creation
        try:
            channel_layer = get_channel_layer()
            update_data = {
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'status': instance.status,
                'status_display': instance.get_status_display(),
                'updated_at': instance.updated_at.isoformat(),
            }

            # Broadcast to order tracking channel
            async_to_sync(channel_layer.group_send)(
                f'order_{instance.id}',
                {
                    'type': 'order_update',
                    'data': update_data
                }
            )

            logger.info(f"Broadcasted order update for {instance.order_number}")

        except Exception as e:
            logger.error(f"Error broadcasting order update: {str(e)}")
