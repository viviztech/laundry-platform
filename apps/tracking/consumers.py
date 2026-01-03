"""
WebSocket consumer for real-time location tracking.
"""

import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import LocationUpdate, Route
from apps.orders.models import Order

logger = logging.getLogger(__name__)


class LocationTrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time GPS tracking.

    URL: ws://localhost:8000/ws/tracking/{order_id}/

    Events:
    - location_update: Real-time location from partner
    - eta_update: ETA updates
    - status_update: Delivery status changes
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'tracking_{self.order_id}'
        self.user = self.scope.get('user')

        # Check if user is authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verify user has access to this order
        has_access = await self.verify_order_access()
        if not has_access:
            await self.close(code=4003)
            return

        # Join tracking group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial location if available
        initial_location = await self.get_latest_location()
        if initial_location:
            await self.send_json({
                'type': 'location_update',
                'location': initial_location
            })

        logger.info(f"User {self.user.id} connected to tracking for order {self.order_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.id if self.user else 'Unknown'} disconnected from tracking {self.order_id}")

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type')

        if message_type == 'location_update':
            # Only partners can send location updates
            if await self.is_partner():
                await self.handle_location_update(content)
        elif message_type == 'request_location':
            # Request latest location
            await self.send_latest_location()
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def handle_location_update(self, content):
        """Handle location update from partner."""
        latitude = content.get('latitude')
        longitude = content.get('longitude')

        if not latitude or not longitude:
            return

        # Save location update
        location_data = await self.save_location_update(content)

        if location_data:
            # Broadcast to all connected clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'location': location_data
                }
            )

    async def send_latest_location(self):
        """Send the latest location to requesting client."""
        location = await self.get_latest_location()
        if location:
            await self.send_json({
                'type': 'location_update',
                'location': location
            })

    # Event handlers for messages from channel layer

    async def location_update(self, event):
        """Send location update to WebSocket."""
        await self.send_json(event['location'])

    async def eta_update(self, event):
        """Send ETA update to WebSocket."""
        await self.send_json({
            'type': 'eta_update',
            'eta': event['eta'],
            'estimated_arrival': event['estimated_arrival']
        })

    async def status_update(self, event):
        """Send status update to WebSocket."""
        await self.send_json({
            'type': 'status_update',
            'status': event['status'],
            'message': event.get('message', '')
        })

    # Database operations

    @database_sync_to_async
    def verify_order_access(self):
        """Verify user has access to the order."""
        try:
            order = Order.objects.get(id=self.order_id)
            if self.user == order.customer:
                return True
            if hasattr(order, 'assigned_partner') and order.assigned_partner:
                if self.user == order.assigned_partner.user:
                    return True
            return False
        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def is_partner(self):
        """Check if user is a partner."""
        from apps.partners.models import Partner
        try:
            Partner.objects.get(user=self.user)
            return True
        except Partner.DoesNotExist:
            return False

    @database_sync_to_async
    def save_location_update(self, data):
        """Save location update to database."""
        try:
            from apps.partners.models import Partner

            order = Order.objects.get(id=self.order_id)
            partner = Partner.objects.get(user=self.user)

            location = LocationUpdate.objects.create(
                order=order,
                partner=partner,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                accuracy=data.get('accuracy'),
                altitude=data.get('altitude'),
                speed=data.get('speed'),
                heading=data.get('heading'),
                address=data.get('address', ''),
                status=data.get('status', 'in_transit'),
                metadata=data.get('metadata', {})
            )

            # Update route ETA if exists
            try:
                route = Route.objects.get(order=order, is_active=True)
                if location.speed:
                    route.update_eta(
                        float(location.latitude),
                        float(location.longitude),
                        location.speed
                    )
            except Route.DoesNotExist:
                pass

            return location.to_geojson()
        except Exception as e:
            logger.error(f"Error saving location update: {e}")
            return None

    @database_sync_to_async
    def get_latest_location(self):
        """Get the latest location update for the order."""
        try:
            location = LocationUpdate.objects.filter(
                order_id=self.order_id
            ).select_related('partner').first()

            if location:
                return location.to_geojson()
            return None
        except Exception as e:
            logger.error(f"Error getting latest location: {e}")
            return None
