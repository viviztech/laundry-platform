"""
WebSocket consumers for real-time features.
Handles WebSocket connections for notifications, order tracking, and partner updates.
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.

    Receives and sends notification updates to authenticated users.
    Each user has their own channel group: user_{user_id}
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Only allow authenticated users to connect.
        """
        self.user = self.scope['user']

        # Reject unauthenticated connections
        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning("Unauthenticated WebSocket connection attempt")
            await self.close(code=4001)  # Custom close code for auth failure
            return

        # Create unique group name for this user
        self.group_name = f'user_{self.user.id}'

        # Join user's personal notification channel
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        logger.info(f"Notification WebSocket connected for user {self.user.id}")

        # Send initial data: unread notification count
        unread_count = await self.get_unread_count()
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to notification stream',
            'unread_count': unread_count
        })

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Notification WebSocket disconnected for user {self.user.id}, code: {close_code}")

    async def receive_json(self, content):
        """
        Handle incoming WebSocket messages from client.

        Supported message types:
        - mark_read: Mark a notification as read
        - mark_all_read: Mark all notifications as read
        - ping: Keep-alive ping
        """
        message_type = content.get('type')

        try:
            if message_type == 'mark_read':
                notification_id = content.get('notification_id')
                success = await self.mark_notification_read(notification_id)

                await self.send_json({
                    'type': 'mark_read_response',
                    'notification_id': notification_id,
                    'success': success
                })

            elif message_type == 'mark_all_read':
                count = await self.mark_all_notifications_read()

                await self.send_json({
                    'type': 'mark_all_read_response',
                    'marked_count': count,
                    'success': True
                })

            elif message_type == 'ping':
                await self.send_json({
                    'type': 'pong',
                    'timestamp': content.get('timestamp')
                })

            else:
                await self.send_json({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
            await self.send_json({
                'type': 'error',
                'message': 'Internal server error'
            })

    # ===== Message Handlers (receive from channel layer) =====

    async def notification_message(self, event):
        """
        Handle notification broadcast from channel layer.
        Send notification to connected client.
        """
        await self.send_json({
            'type': 'notification',
            'notification': event['notification']
        })

    async def unread_count_update(self, event):
        """
        Handle unread count update from channel layer.
        """
        await self.send_json({
            'type': 'unread_count',
            'count': event['count']
        })

    # ===== Database Operations =====

    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for user."""
        from apps.notifications.utils import get_unread_count
        return get_unread_count(self.user)

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a single notification as read."""
        from apps.notifications.models import Notification
        from django.utils import timezone

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user.id}")
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all user notifications as read."""
        from apps.notifications.utils import mark_all_as_read
        return mark_all_as_read(self.user)


class OrderTrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time order tracking.

    Allows users to track specific orders in real-time.
    Users can only track their own orders (or orders assigned to them if they're partners).
    """

    async def connect(self):
        """
        Handle WebSocket connection for order tracking.
        """
        self.user = self.scope['user']
        self.order_id = self.scope['url_route']['kwargs']['order_id']

        # Reject unauthenticated connections
        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning("Unauthenticated order tracking connection attempt")
            await self.close(code=4001)
            return

        # Check if user has access to this order
        has_access = await self.can_access_order()
        if not has_access:
            logger.warning(f"User {self.user.id} attempted to access order {self.order_id} without permission")
            await self.close(code=4003)  # Forbidden
            return

        # Create group name for this order
        self.group_name = f'order_{self.order_id}'

        # Join order tracking channel
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        logger.info(f"Order tracking WebSocket connected for user {self.user.id}, order {self.order_id}")

        # Send current order status
        order_data = await self.get_order_data()
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to order tracking',
            'order': order_data
        })

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Order tracking WebSocket disconnected for order {self.order_id}, code: {close_code}")

    async def receive_json(self, content):
        """
        Handle incoming messages (currently just ping/pong for keep-alive).
        """
        message_type = content.get('type')

        if message_type == 'ping':
            await self.send_json({
                'type': 'pong',
                'timestamp': content.get('timestamp')
            })

    # ===== Message Handlers =====

    async def order_update(self, event):
        """
        Handle order status update from channel layer.
        """
        await self.send_json({
            'type': 'order_update',
            'update': event['data']
        })

    async def location_update(self, event):
        """
        Handle location update from channel layer (for delivery tracking).
        """
        await self.send_json({
            'type': 'location',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp']
        })

    # ===== Database Operations =====

    @database_sync_to_async
    def can_access_order(self):
        """
        Check if user can access this order.
        Users can access orders if they:
        - Created the order (customer)
        - Are assigned to the order (partner)
        - Are admin
        """
        from apps.orders.models import Order

        try:
            order = Order.objects.select_related('partner').get(id=self.order_id)

            # Customer can access their own orders
            if order.user_id == self.user.id:
                return True

            # Partner can access assigned orders
            if hasattr(self.user, 'partner') and order.partner_id == self.user.partner.id:
                return True

            # Admin can access all orders
            if self.user.is_staff or self.user.is_superuser:
                return True

            return False

        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def get_order_data(self):
        """
        Get current order data.
        """
        from apps.orders.models import Order

        try:
            order = Order.objects.select_related('partner', 'address').get(id=self.order_id)

            return {
                'id': str(order.id),
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'pickup_date': order.pickup_date.isoformat() if order.pickup_date else None,
                'delivery_date': order.delivery_date.isoformat() if order.delivery_date else None,
                'total_amount': str(order.total_amount),
                'partner': {
                    'id': str(order.partner.id),
                    'name': order.partner.business_name
                } if order.partner else None,
                'updated_at': order.updated_at.isoformat()
            }
        except Order.DoesNotExist:
            return None


class PartnerConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for partner real-time updates.

    Receives:
    - New order assignments
    - Customer messages
    - Earnings updates
    """

    async def connect(self):
        """
        Handle WebSocket connection for partners.
        """
        self.user = self.scope['user']

        # Reject unauthenticated connections
        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning("Unauthenticated partner connection attempt")
            await self.close(code=4001)
            return

        # Check if user is a partner
        is_partner = await self.is_partner_user()
        if not is_partner:
            logger.warning(f"Non-partner user {self.user.id} attempted to connect to partner channel")
            await self.close(code=4003)  # Forbidden
            return

        # Create group name for this partner
        partner_id = await self.get_partner_id()
        self.group_name = f'partner_{partner_id}'

        # Join partner channel
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        logger.info(f"Partner WebSocket connected for user {self.user.id}, partner {partner_id}")

        # Send confirmation
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to partner stream'
        })

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Partner WebSocket disconnected, code: {close_code}")

    async def receive_json(self, content):
        """
        Handle incoming messages from partner.
        """
        message_type = content.get('type')

        if message_type == 'ping':
            await self.send_json({
                'type': 'pong',
                'timestamp': content.get('timestamp')
            })

    # ===== Message Handlers =====

    async def new_order_assignment(self, event):
        """
        Handle new order assignment notification.
        """
        await self.send_json({
            'type': 'new_order',
            'order': event['order_data']
        })

    async def earnings_update(self, event):
        """
        Handle earnings update.
        """
        await self.send_json({
            'type': 'earnings_update',
            'amount': event['amount'],
            'total': event['total']
        })

    # ===== Database Operations =====

    @database_sync_to_async
    def is_partner_user(self):
        """
        Check if user has an associated partner profile.
        """
        return hasattr(self.user, 'partner')

    @database_sync_to_async
    def get_partner_id(self):
        """
        Get partner ID for the user.
        """
        if hasattr(self.user, 'partner'):
            return str(self.user.partner.id)
        return None
