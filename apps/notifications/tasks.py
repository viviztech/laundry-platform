"""
Celery tasks for sending notifications.
"""
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, notification_id):
    """
    Send web push notification asynchronously.

    Args:
        notification_id: UUID of the notification to send

    Returns:
        Boolean indicating success
    """
    from .models import Notification, PushSubscription
    from .push import push_service

    try:
        notification = Notification.objects.select_related(
            'user', 'order', 'payment'
        ).get(id=notification_id)

        # Check if push service is enabled
        if not push_service.is_enabled():
            logger.warning('Push notification service is not configured. Skipping push.')
            return False

        # Check user preferences for push notifications
        from .utils import should_send_push_notification
        if not should_send_push_notification(notification.user, notification.type):
            logger.info(
                f'Skipping push for notification {notification.notification_id} - '
                f'user preferences disabled'
            )
            return False

        # Get active push subscriptions for user
        subscriptions = PushSubscription.objects.filter(
            user=notification.user,
            is_active=True
        )

        if not subscriptions.exists():
            logger.info(
                f'No active push subscriptions for user {notification.user.email}'
            )
            return False

        # Prepare push notification data
        push_data = {
            'title': notification.title,
            'body': notification.message,
            'icon': '/static/images/logo-192x192.png',
            'badge': '/static/images/badge-72x72.png',
            'tag': f'notification-{notification.notification_id}',
            'data': {
                'notification_id': str(notification.id),
                'url': notification.action_url or '/',
                'type': notification.type,
            }
        }

        # Send to all active subscriptions
        success_count = 0
        failed_count = 0
        expired_endpoints = []

        for subscription in subscriptions:
            result = push_service.send_push_notification(
                subscription.get_subscription_info(),
                push_data
            )

            if result['success']:
                success_count += 1
                # Update last used timestamp
                subscription.last_used_at = timezone.now()
                subscription.save(update_fields=['last_used_at'])
            else:
                failed_count += 1
                error = result.get('error', '')

                # Handle expired subscriptions
                if 'expired' in error.lower() or 'gone' in error.lower():
                    expired_endpoints.append(subscription.endpoint)
                    subscription.is_active = False
                    subscription.save(update_fields=['is_active'])
                    logger.warning(
                        f'Push subscription expired for user {notification.user.email}: '
                        f'{subscription.endpoint[:50]}...'
                    )

        # Deactivate expired subscriptions
        if expired_endpoints:
            PushSubscription.objects.filter(
                endpoint__in=expired_endpoints
            ).update(is_active=False)

        # Store push metadata in notification
        if not notification.metadata:
            notification.metadata = {}

        notification.metadata['push'] = {
            'sent': success_count > 0,
            'success_count': success_count,
            'failed_count': failed_count,
            'total_subscriptions': subscriptions.count(),
            'sent_at': timezone.now().isoformat(),
        }
        notification.save(update_fields=['metadata'])

        if success_count > 0:
            logger.info(
                f'Push notification sent successfully for {notification.notification_id}. '
                f'Delivered to {success_count}/{subscriptions.count()} subscriptions.'
            )
            return True
        else:
            logger.warning(
                f'Push notification failed for {notification.notification_id}. '
                f'All {failed_count} attempts failed.'
            )
            return False

    except Notification.DoesNotExist:
        logger.error(f'Notification not found: {notification_id}')
        return False

    except Exception as e:
        logger.error(f'Unexpected error in send_push_notification: {str(e)}')
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_notification_sms(self, notification_id):
    """
    Send SMS for a notification asynchronously.

    Args:
        notification_id: UUID of the notification to send

    Returns:
        Boolean indicating success
    """
    from .models import Notification
    from .sms import sms_service

    try:
        notification = Notification.objects.select_related(
            'user', 'order', 'payment'
        ).get(id=notification_id)

        # Check if SMS service is enabled
        if not sms_service.is_enabled():
            logger.warning('SMS service is not configured. Skipping SMS.')
            return False

        # Check if user has phone number
        if not hasattr(notification.user, 'phone') or not notification.user.phone:
            logger.info(
                f'User {notification.user.email} has no phone number. Skipping SMS.'
            )
            return False

        # Build context for SMS
        from .utils import build_email_context
        context = build_email_context(notification)
        context['notification_id'] = str(notification.id)

        # Send SMS
        result = sms_service.send_notification_sms(
            user=notification.user,
            notification_type=notification.type,
            context=context
        )

        if result['success']:
            logger.info(
                f'SMS sent successfully for notification {notification.notification_id}. '
                f'SID: {result["message_sid"]}'
            )

            # Store SMS metadata in notification
            if not notification.metadata:
                notification.metadata = {}

            notification.metadata['sms'] = {
                'sent': True,
                'message_sid': result['message_sid'],
                'sent_at': timezone.now().isoformat(),
                'status': result['status'],
                'to': result.get('to'),
            }
            notification.save(update_fields=['metadata'])

            return True
        else:
            logger.warning(
                f'SMS sending failed for notification {notification.notification_id}: '
                f'{result.get("error")}'
            )

            # Store error in metadata
            if not notification.metadata:
                notification.metadata = {}

            notification.metadata['sms'] = {
                'sent': False,
                'error': result.get('error'),
                'attempted_at': timezone.now().isoformat(),
            }
            notification.save(update_fields=['metadata'])

            # Retry if it's a temporary error (not user preference or missing phone)
            if result.get('status') not in ['disabled_by_user', 'failed']:
                raise self.retry(exc=Exception(result.get('error')), countdown=300)

            return False

    except Notification.DoesNotExist:
        logger.error(f'Notification not found: {notification_id}')
        return False

    except Exception as e:
        logger.error(f'Unexpected error in send_notification_sms: {str(e)}')
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """
    Send email for a notification asynchronously.

    Args:
        notification_id: UUID of the notification to send

    Returns:
        Boolean indicating success
    """
    from .models import Notification, NotificationTemplate
    from .utils import build_email_context, should_send_email_notification

    try:
        notification = Notification.objects.select_related(
            'user', 'order', 'payment'
        ).get(id=notification_id)

        # Check if email should be sent
        if not should_send_email_notification(notification.user, notification.type):
            logger.info(
                f'Skipping email for notification {notification.notification_id} - '
                f'user preferences disabled'
            )
            return False

        # Check if already sent
        if notification.email_sent:
            logger.warning(
                f'Email already sent for notification {notification.notification_id}'
            )
            return False

        # Get email template
        try:
            template = NotificationTemplate.objects.get(
                type=notification.type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            logger.error(
                f'No active template found for notification type: {notification.type}'
            )
            notification.email_error = 'No template found'
            notification.save(update_fields=['email_error'])
            return False

        # Build context for email
        context = build_email_context(notification)

        # Render email subject and body
        try:
            from django.template import Template, Context
            subject_template = Template(template.email_subject)
            subject = subject_template.render(Context(context))

            html_template = Template(template.email_body_html)
            html_body = html_template.render(Context(context))

            text_template = Template(template.email_body_text)
            text_body = text_template.render(Context(context))

        except Exception as e:
            logger.error(f'Template rendering error: {str(e)}')
            notification.email_error = f'Template rendering error: {str(e)}'
            notification.save(update_fields=['email_error'])
            raise self.retry(exc=e, countdown=60)

        # Send email
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[notification.user.email],
            )
            email.attach_alternative(html_body, "text/html")
            email.send()

            # Update notification
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.email_error = ''
            notification.save(update_fields=[
                'email_sent', 'email_sent_at', 'email_error'
            ])

            logger.info(
                f'Email sent successfully for notification {notification.notification_id}'
            )
            return True

        except Exception as e:
            logger.error(f'Email sending error: {str(e)}')
            notification.email_error = str(e)
            notification.save(update_fields=['email_error'])
            raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes

    except Notification.DoesNotExist:
        logger.error(f'Notification not found: {notification_id}')
        return False

    except Exception as e:
        logger.error(f'Unexpected error in send_notification_email: {str(e)}')
        raise self.retry(exc=e, countdown=300)


@shared_task
def send_bulk_notifications(user_ids, notification_type, context_data=None):
    """
    Send notifications to multiple users.

    Args:
        user_ids: List of user IDs to send to
        notification_type: Type of notification
        context_data: Optional context data for notification

    Returns:
        Number of notifications created
    """
    from django.contrib.auth import get_user_model
    from .utils import create_notification

    User = get_user_model()
    context_data = context_data or {}

    count = 0
    for user_id in user_ids:
        try:
            user = User.objects.get(id=user_id)
            create_notification(
                user=user,
                notification_type=notification_type,
                extra_context=context_data
            )
            count += 1
        except User.DoesNotExist:
            logger.warning(f'User not found: {user_id}')
            continue
        except Exception as e:
            logger.error(f'Error creating notification for user {user_id}: {str(e)}')
            continue

    logger.info(f'Created {count} bulk notifications of type {notification_type}')
    return count


@shared_task
def cleanup_old_notifications(days=30):
    """
    Delete read notifications older than specified days.

    Args:
        days: Number of days to keep notifications

    Returns:
        Number of notifications deleted
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Notification

    cutoff_date = timezone.now() - timedelta(days=days)

    count, _ = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff_date
    ).delete()

    logger.info(f'Deleted {count} old notifications')
    return count


@shared_task
def send_daily_summary_email(user_id):
    """
    Send daily summary of unread notifications to a user.

    Args:
        user_id: User ID to send summary to

    Returns:
        Boolean indicating success
    """
    from django.contrib.auth import get_user_model
    from .models import Notification
    from .utils import should_send_email_notification

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        # Check if user wants email notifications
        if not should_send_email_notification(user, 'general'):
            return False

        # Get unread notifications
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        ).order_by('-created_at')[:10]

        if not unread_notifications:
            return False

        # Render summary email
        context = {
            'user': user,
            'notifications': unread_notifications,
            'count': unread_notifications.count(),
        }

        subject = f'You have {context["count"]} unread notifications'
        html_body = render_to_string(
            'emails/daily_summary.html',
            context
        )
        text_body = render_to_string(
            'emails/daily_summary.txt',
            context
        )

        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_body, "text/html")
        email.send()

        logger.info(f'Daily summary sent to {user.email}')
        return True

    except User.DoesNotExist:
        logger.error(f'User not found: {user_id}')
        return False
    except Exception as e:
        logger.error(f'Error sending daily summary: {str(e)}')
        return False
