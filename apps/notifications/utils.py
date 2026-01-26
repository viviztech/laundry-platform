"""
Utility functions for notification system.
"""
from django.template import Template, Context
from .models import Notification, NotificationTemplate, NotificationPreference


def create_notification(user, notification_type, order=None, payment=None, **kwargs):
    """
    Create a notification and optionally send email.

    Args:
        user: User to send notification to
        notification_type: Type of notification
        order: Optional related order
        payment: Optional related payment
        **kwargs: Additional fields for notification

    Returns:
        Created Notification instance
    """
    # Get template for this notification type
    try:
        template = NotificationTemplate.objects.get(
            type=notification_type,
            is_active=True
        )
    except NotificationTemplate.DoesNotExist:
        # No template found, create basic notification
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=f'Notification: {notification_type}',
            message=f'You have a new {notification_type} notification.',
            order=order,
            payment=payment,
            **kwargs
        )
        return notification

    # Build context for template rendering
    context = {
        'user': user,
        'order': order,
        'payment': payment,
    }
    context.update(kwargs.get('extra_context', {}))

    # Render title and message
    title = render_template(template.title_template, context)
    message = render_template(template.message_template, context)

    # Generate action URL if template has one
    action_url = ''
    if template.action_url_template:
        action_url = render_template(template.action_url_template, context)

    # Create notification
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        order=order,
        payment=payment,
        action_url=action_url,
        metadata=kwargs.get('metadata', {}),
    )

    # Check if we should send email
    should_send = should_send_email_notification(user, notification_type)

    if should_send:
        # Queue async email task
        from .tasks import send_notification_email
        send_notification_email.delay(str(notification.id))

    return notification


def render_template(template_string, context):
    """
    Render a Django template string with context.

    Args:
        template_string: Template string with {{ variables }}
        context: Dictionary of variables

    Returns:
        Rendered string
    """
    try:
        template = Template(template_string)
        return template.render(Context(context))
    except Exception as e:
        # Fallback to template string if rendering fails
        return template_string


def should_send_email_notification(user, notification_type):
    """
    Check if email should be sent for this notification type.

    Args:
        user: User to check preferences for
        notification_type: Type of notification

    Returns:
        Boolean indicating if email should be sent
    """
    # Check global user profile preference
    if hasattr(user, 'profile') and not user.profile.receive_notifications:
        return False

    # Get notification preferences
    try:
        prefs = NotificationPreference.objects.get(user=user)
        return prefs.should_send_email(notification_type)
    except NotificationPreference.DoesNotExist:
        # Default to sending if no preferences set
        return True


def should_send_push_notification(user, notification_type):
    """
    Check if push notification should be sent for this notification type.

    Args:
        user: User to check preferences for
        notification_type: Type of notification

    Returns:
        Boolean indicating if push should be sent
    """
    # Check global user profile preference
    if hasattr(user, 'profile') and not user.profile.receive_notifications:
        return False

    # Get notification preferences
    try:
        prefs = NotificationPreference.objects.get(user=user)
        return prefs.should_send_push(notification_type)
    except NotificationPreference.DoesNotExist:
        # Default to sending if no preferences set
        return True


def build_email_context(notification):
    """
    Build context dictionary for email templates.

    Args:
        notification: Notification instance

    Returns:
        Dictionary with template context
    """
    context = {
        'notification': notification,
        'user': notification.user,
        'order': notification.order,
        'payment': notification.payment,
        'title': notification.title,
        'message': notification.message,
        'action_url': notification.action_url,
    }

    # Add order details if available
    if notification.order:
        context.update({
            'order_number': notification.order.order_number,
            'order_status': notification.order.get_status_display(),
            'order_total': notification.order.total_amount,
            'pickup_date': notification.order.pickup_date,
        })

    # Add payment details if available
    if notification.payment:
        context.update({
            'payment_id': notification.payment.payment_id,
            'payment_amount': notification.payment.amount,
            'payment_status': notification.payment.get_status_display(),
            'payment_method': notification.payment.get_method_display(),
        })

    return context


def get_unread_count(user):
    """
    Get count of unread notifications for a user.

    Args:
        user: User instance

    Returns:
        Integer count of unread notifications
    """
    return Notification.objects.filter(
        user=user,
        is_read=False
    ).count()


def mark_all_as_read(user):
    """
    Mark all notifications as read for a user.

    Args:
        user: User instance

    Returns:
        Number of notifications marked as read
    """
    from django.utils import timezone

    count = Notification.objects.filter(
        user=user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )

    return count
