"""
SMS notification service for LaundryConnect platform.
Handles sending SMS notifications via Twilio.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)
User = get_user_model()


class SMSService:
    """
    Service for sending SMS notifications via Twilio.

    Features:
    - Send SMS to users
    - Template-based SMS messages
    - Delivery tracking
    - Error handling and logging
    - Cost tracking
    """

    def __init__(self):
        """Initialize Twilio client with credentials from settings."""
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning(
                "Twilio credentials not configured. SMS notifications will be disabled. "
                "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in settings."
            )
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)

    def is_enabled(self) -> bool:
        """Check if SMS service is properly configured."""
        return self.client is not None

    def send_sms(
        self,
        to_number: str,
        message: str,
        notification_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS to a phone number.

        Args:
            to_number: Recipient phone number (E.164 format: +919876543210)
            message: SMS message content (max 1600 characters for long messages)
            notification_id: Optional notification ID for tracking

        Returns:
            Dict with keys:
                - success (bool): Whether SMS was sent successfully
                - message_sid (str): Twilio message SID if successful
                - error (str): Error message if failed
                - status (str): Twilio message status
                - cost (str): Message cost if available
        """
        if not self.is_enabled():
            logger.error("SMS service is not enabled. Check Twilio configuration.")
            return {
                'success': False,
                'error': 'SMS service not configured',
                'message_sid': None,
                'status': 'failed'
            }

        # Validate phone number format
        if not to_number.startswith('+'):
            logger.error(f"Invalid phone number format: {to_number}. Must be in E.164 format (+country_code...)")
            return {
                'success': False,
                'error': 'Invalid phone number format. Must start with + and country code.',
                'message_sid': None,
                'status': 'failed'
            }

        # Validate message length
        if len(message) > 1600:
            logger.warning(f"Message too long ({len(message)} chars). Truncating to 1600 characters.")
            message = message[:1597] + '...'

        try:
            # Send SMS via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
                status_callback=getattr(settings, 'TWILIO_STATUS_CALLBACK_URL', None)
            )

            logger.info(
                f"SMS sent successfully. SID: {twilio_message.sid}, "
                f"To: {to_number}, Notification: {notification_id}"
            )

            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'error': None,
                'to': twilio_message.to,
                'from': twilio_message.from_,
                'date_created': twilio_message.date_created,
                'price': twilio_message.price,
                'price_unit': twilio_message.price_unit,
            }

        except TwilioRestException as e:
            logger.error(
                f"Twilio error sending SMS to {to_number}: {e.msg} (Code: {e.code})",
                exc_info=True
            )
            return {
                'success': False,
                'error': f"Twilio error: {e.msg}",
                'message_sid': None,
                'status': 'failed',
                'error_code': e.code
            }

        except Exception as e:
            logger.error(
                f"Unexpected error sending SMS to {to_number}: {str(e)}",
                exc_info=True
            )
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'message_sid': None,
                'status': 'failed'
            }

    def send_notification_sms(
        self,
        user: User,
        notification_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send SMS notification to a user based on notification type.

        Args:
            user: User instance to send SMS to
            notification_type: Type of notification (e.g., 'order_confirmed')
            context: Context data for rendering the SMS template

        Returns:
            Dict with SMS sending result
        """
        # Check if user has phone number
        if not hasattr(user, 'phone') or not user.phone:
            logger.warning(f"User {user.email} has no phone number. Cannot send SMS.")
            return {
                'success': False,
                'error': 'User has no phone number',
                'message_sid': None,
                'status': 'failed'
            }

        # Check user SMS preferences
        from apps.notifications.models import NotificationPreference

        try:
            preferences = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            preferences = NotificationPreference.objects.create(user=user)

        # Check if user wants SMS for this notification type
        if not self._should_send_sms(preferences, notification_type):
            logger.info(f"User {user.email} has disabled SMS for {notification_type}")
            return {
                'success': False,
                'error': 'User has disabled SMS notifications',
                'message_sid': None,
                'status': 'disabled_by_user'
            }

        # Get SMS template
        message = self._get_sms_message(notification_type, context)

        if not message:
            logger.error(f"No SMS template found for notification type: {notification_type}")
            return {
                'success': False,
                'error': 'No SMS template found',
                'message_sid': None,
                'status': 'failed'
            }

        # Send SMS
        notification_id = context.get('notification_id')
        return self.send_sms(
            to_number=user.phone,
            message=message,
            notification_id=notification_id
        )

    def _should_send_sms(self, preferences, notification_type: str) -> bool:
        """
        Check if SMS should be sent based on user preferences.

        Args:
            preferences: NotificationPreference instance
            notification_type: Type of notification

        Returns:
            bool: True if SMS should be sent
        """
        # Critical notifications that should always be sent via SMS if enabled
        critical_types = [
            'order_confirmed',
            'order_out_for_delivery',
            'order_delivered',
            'payment_completed',
            'refund_completed',
        ]

        # Map notification types to preference fields
        if notification_type.startswith('order_'):
            return preferences.order_updates_sms
        elif notification_type.startswith('payment_'):
            return preferences.payment_updates_sms
        elif notification_type in critical_types:
            # For critical notifications, check general SMS preferences
            return preferences.order_updates_sms or preferences.payment_updates_sms

        return False

    def _get_sms_message(self, notification_type: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Get SMS message for a notification type.

        Args:
            notification_type: Type of notification
            context: Context data for rendering template

        Returns:
            str: Rendered SMS message or None if template not found
        """
        from apps.notifications.models import NotificationTemplate
        from django.template import Template, Context

        try:
            template = NotificationTemplate.objects.get(type=notification_type, is_active=True)

            if not template.sms_template:
                logger.warning(f"SMS template not defined for {notification_type}")
                return None

            # Render template with context
            django_template = Template(template.sms_template)
            rendered_message = django_template.render(Context(context))

            return rendered_message.strip()

        except NotificationTemplate.DoesNotExist:
            logger.warning(f"No notification template found for type: {notification_type}")
            return None

    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get the status of a sent SMS message.

        Args:
            message_sid: Twilio message SID

        Returns:
            Dict with message status information
        """
        if not self.is_enabled():
            return {'error': 'SMS service not configured'}

        try:
            message = self.client.messages(message_sid).fetch()

            return {
                'success': True,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated,
                'price': message.price,
                'price_unit': message.price_unit,
            }

        except TwilioRestException as e:
            logger.error(f"Error fetching message status: {e.msg}")
            return {
                'success': False,
                'error': e.msg,
                'error_code': e.code
            }

    def verify_phone_number(self, phone_number: str) -> bool:
        """
        Verify if a phone number is valid using Twilio Lookup API.

        Args:
            phone_number: Phone number to verify (E.164 format)

        Returns:
            bool: True if phone number is valid
        """
        if not self.is_enabled():
            logger.warning("SMS service not enabled. Cannot verify phone number.")
            return False

        try:
            # Use Twilio Lookup API to validate phone number
            from twilio.rest.lookups import LookupsClient

            lookups_client = LookupsClient(self.account_sid, self.auth_token)
            phone_info = lookups_client.phone_numbers(phone_number).fetch()

            logger.info(f"Phone number verified: {phone_info.phone_number}")
            return True

        except TwilioRestException as e:
            logger.warning(f"Phone number validation failed: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"Error validating phone number: {str(e)}")
            return False


# Global SMS service instance
sms_service = SMSService()


def send_sms_notification(user: User, notification_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to send SMS notification.

    Args:
        user: User to send SMS to
        notification_type: Type of notification
        context: Context data for template rendering

    Returns:
        Dict with SMS sending result
    """
    return sms_service.send_notification_sms(user, notification_type, context)
