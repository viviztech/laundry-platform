"""
Push notification service for LaundryConnect platform.
Handles sending browser push notifications using Web Push API and VAPID.
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)
User = get_user_model()


class PushNotificationService:
    """
    Service for sending browser push notifications using Web Push API.

    Features:
    - Send push notifications to subscribed browsers
    - Multi-device support per user
    - Rich notifications with images and actions
    - VAPID authentication
    - Delivery tracking
    """

    def __init__(self):
        """Initialize push notification service with VAPID credentials."""
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
        self.vapid_admin_email = getattr(settings, 'VAPID_ADMIN_EMAIL', 'mailto:admin@laundryconnect.com')

        if not all([self.vapid_private_key, self.vapid_public_key]):
            logger.warning(
                "VAPID keys not configured. Push notifications will be disabled. "
                "Set VAPID_PRIVATE_KEY and VAPID_PUBLIC_KEY in settings."
            )

    def is_enabled(self) -> bool:
        """Check if push notification service is properly configured."""
        return bool(self.vapid_private_key and self.vapid_public_key)

    def send_push_notification(
        self,
        subscription_info: Dict[str, Any],
        notification_data: Dict[str, Any],
        ttl: int = 86400
    ) -> Dict[str, Any]:
        """
        Send push notification to a browser subscription.

        Args:
            subscription_info: Browser push subscription info
                {
                    'endpoint': 'https://...',
                    'keys': {
                        'p256dh': '...',
                        'auth': '...'
                    }
                }
            notification_data: Notification payload
                {
                    'title': 'Notification Title',
                    'body': 'Notification message',
                    'icon': '/static/images/icon.png',
                    'badge': '/static/images/badge.png',
                    'image': '/static/images/order.jpg',
                    'data': {'url': '/orders/123', 'order_id': '123'},
                    'actions': [
                        {'action': 'view', 'title': 'View Order'},
                        {'action': 'dismiss', 'title': 'Dismiss'}
                    ]
                }
            ttl: Time-to-live in seconds (default: 24 hours)

        Returns:
            Dict with keys:
                - success (bool): Whether push was sent successfully
                - status_code (int): HTTP status code if successful
                - error (str): Error message if failed
        """
        if not self.is_enabled():
            logger.error("Push notification service is not enabled. Check VAPID configuration.")
            return {
                'success': False,
                'error': 'Push notification service not configured',
                'status_code': None
            }

        try:
            # Prepare VAPID claims
            vapid_claims = {
                "sub": self.vapid_admin_email
            }

            # Send push notification
            response = webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=vapid_claims,
                ttl=ttl
            )

            logger.info(
                f"Push notification sent successfully. "
                f"Status: {response.status_code}, Endpoint: {subscription_info.get('endpoint', '')[:50]}..."
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'error': None
            }

        except WebPushException as e:
            # Handle specific Web Push errors
            if e.response and e.response.status_code == 410:
                # Subscription expired or invalid (410 Gone)
                logger.warning(f"Push subscription expired: {str(e)}")
                return {
                    'success': False,
                    'error': 'Subscription expired',
                    'status_code': 410,
                    'should_delete': True  # Signal to delete this subscription
                }
            elif e.response and e.response.status_code == 404:
                # Subscription not found
                logger.warning(f"Push subscription not found: {str(e)}")
                return {
                    'success': False,
                    'error': 'Subscription not found',
                    'status_code': 404,
                    'should_delete': True
                }
            else:
                logger.error(
                    f"WebPushException sending push notification: {str(e)}, "
                    f"Status: {e.response.status_code if e.response else 'N/A'}",
                    exc_info=True
                )
                return {
                    'success': False,
                    'error': f"WebPush error: {str(e)}",
                    'status_code': e.response.status_code if e.response else None
                }

        except Exception as e:
            logger.error(
                f"Unexpected error sending push notification: {str(e)}",
                exc_info=True
            )
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'status_code': None
            }

    def send_notification_to_user(
        self,
        user: User,
        notification_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send push notification to all of a user's subscribed devices.

        Args:
            user: User instance to send push to
            notification_type: Type of notification (e.g., 'order_confirmed')
            context: Context data for notification

        Returns:
            Dict with:
                - success (bool): Whether at least one push succeeded
                - sent_count (int): Number of successful pushes
                - failed_count (int): Number of failed pushes
                - results (list): Individual results per subscription
        """
        from apps.notifications.models import PushSubscription

        # Get user's active subscriptions
        subscriptions = PushSubscription.objects.filter(
            user=user,
            is_active=True
        )

        if not subscriptions.exists():
            logger.info(f"User {user.email} has no active push subscriptions")
            return {
                'success': False,
                'sent_count': 0,
                'failed_count': 0,
                'results': [],
                'error': 'No active subscriptions'
            }

        # Check user preferences
        if not self._should_send_push(user, notification_type):
            logger.info(f"User {user.email} has disabled push for {notification_type}")
            return {
                'success': False,
                'sent_count': 0,
                'failed_count': 0,
                'results': [],
                'error': 'User has disabled push notifications'
            }

        # Build notification payload
        notification_data = self._build_notification_payload(notification_type, context)

        # Send to all subscriptions
        results = []
        sent_count = 0
        failed_count = 0
        expired_subscriptions = []

        for subscription in subscriptions:
            subscription_info = {
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh_key,
                    'auth': subscription.auth_key
                }
            }

            result = self.send_push_notification(subscription_info, notification_data)
            results.append({
                'subscription_id': str(subscription.id),
                'device_name': subscription.device_name,
                'success': result['success'],
                'error': result.get('error')
            })

            if result['success']:
                sent_count += 1
            else:
                failed_count += 1
                # Mark subscription for deletion if expired
                if result.get('should_delete'):
                    expired_subscriptions.append(subscription)

        # Delete expired subscriptions
        if expired_subscriptions:
            for sub in expired_subscriptions:
                sub.is_active = False
                sub.save(update_fields=['is_active'])
            logger.info(f"Deactivated {len(expired_subscriptions)} expired subscriptions for user {user.email}")

        return {
            'success': sent_count > 0,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'results': results
        }

    def _should_send_push(self, user: User, notification_type: str) -> bool:
        """
        Check if push notification should be sent based on user preferences.

        Args:
            user: User instance
            notification_type: Type of notification

        Returns:
            bool: True if push should be sent
        """
        from apps.notifications.models import NotificationPreference

        try:
            preferences = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            preferences = NotificationPreference.objects.create(user=user)

        # Use the model's method to check push preferences
        return preferences.should_send_push(notification_type)

    def _build_notification_payload(
        self,
        notification_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build notification payload for push.

        Args:
            notification_type: Type of notification
            context: Context data with notification info

        Returns:
            Dict: Notification payload for Web Push API
        """
        # Get title and body from context or use defaults
        title = context.get('title', 'LaundryConnect')
        body = context.get('message', 'You have a new notification')

        # Build action URL
        action_url = context.get('action_url', '/')

        # Get order/payment info for rich data
        order_id = context.get('order_id') or (context.get('order', {}).get('id') if context.get('order') else None)
        payment_id = context.get('payment_id') or (context.get('payment', {}).get('id') if context.get('payment') else None)

        # Build notification payload
        payload = {
            'title': title,
            'body': body,
            'icon': context.get('icon', '/static/images/logo-192x192.png'),
            'badge': context.get('badge', '/static/images/badge-72x72.png'),
            'data': {
                'url': action_url,
                'notification_type': notification_type,
                'timestamp': datetime.now().isoformat(),
                'order_id': str(order_id) if order_id else None,
                'payment_id': str(payment_id) if payment_id else None,
            }
        }

        # Add image for order-related notifications
        if notification_type.startswith('order_') and context.get('image'):
            payload['image'] = context['image']

        # Add action buttons based on notification type
        payload['actions'] = self._get_notification_actions(notification_type)

        # Add tag for notification grouping
        if order_id:
            payload['tag'] = f'order_{order_id}'
        elif payment_id:
            payload['tag'] = f'payment_{payment_id}'
        else:
            payload['tag'] = notification_type

        # Set notification to require interaction for important types
        critical_types = [
            'order_confirmed',
            'order_out_for_delivery',
            'payment_completed',
            'refund_completed'
        ]
        if notification_type in critical_types:
            payload['requireInteraction'] = True

        return payload

    def _get_notification_actions(self, notification_type: str) -> list:
        """
        Get action buttons for notification based on type.

        Args:
            notification_type: Type of notification

        Returns:
            list: Action buttons for the notification
        """
        # Common actions for order notifications
        if notification_type.startswith('order_'):
            if notification_type == 'order_delivered':
                return [
                    {'action': 'rate', 'title': 'Rate Service'},
                    {'action': 'view', 'title': 'View Details'}
                ]
            else:
                return [
                    {'action': 'track', 'title': 'Track Order'},
                    {'action': 'view', 'title': 'View Details'}
                ]

        # Payment notifications
        elif notification_type.startswith('payment_'):
            return [
                {'action': 'receipt', 'title': 'View Receipt'},
                {'action': 'dismiss', 'title': 'Dismiss'}
            ]

        # Default actions
        return [
            {'action': 'view', 'title': 'View'},
            {'action': 'dismiss', 'title': 'Dismiss'}
        ]


# Global push notification service instance
push_service = PushNotificationService()


def send_push_to_user(user: User, notification_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to send push notification to a user.

    Args:
        user: User to send push to
        notification_type: Type of notification
        context: Context data for notification

    Returns:
        Dict with push sending results
    """
    return push_service.send_notification_to_user(user, notification_type, context)
