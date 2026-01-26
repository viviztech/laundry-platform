"""
WebSocket consumers for real-time chat functionality.
"""

import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import ChatRoom, ChatMessage, TypingIndicator
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time chat.

    URL: ws://localhost:8000/ws/chat/<room_id>/

    Events:
    - message: Send/receive chat messages
    - typing: Typing indicators
    - read_receipt: Message read receipts
    - delivery_receipt: Message delivery receipts
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope.get('user')

        # Check if user is authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verify user has access to this chat room
        has_access = await self.verify_room_access()
        if not has_access:
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send user_joined event to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name() or self.user.email,
            }
        )

        logger.info(f"User {self.user.id} connected to chat room {self.room_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            # Send user_left event to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': str(self.user.id) if self.user else None,
                    'user_name': self.user.get_full_name() or self.user.email if self.user else 'Unknown',
                }
            )

            # Remove typing indicator
            if self.user:
                await self.remove_typing_indicator()

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"User {self.user.id if self.user else 'Unknown'} disconnected from chat room {self.room_id}")

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(content)
        elif message_type == 'typing_start':
            await self.handle_typing_start(content)
        elif message_type == 'typing_stop':
            await self.handle_typing_stop(content)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(content)
        elif message_type == 'delivery_receipt':
            await self.handle_delivery_receipt(content)
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def handle_chat_message(self, content):
        """Handle incoming chat message."""
        message_text = content.get('message', '').strip()
        message_type = content.get('message_type', 'text')
        metadata = content.get('metadata', {})

        if not message_text and message_type == 'text':
            return

        # Save message to database
        message = await self.save_message(message_text, message_type, metadata)

        if message:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

    async def handle_typing_start(self, content):
        """Handle typing start event."""
        await self.set_typing_indicator()

        # Broadcast typing indicator to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'is_typing': True,
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name() or self.user.email,
            }
        )

    async def handle_typing_stop(self, content):
        """Handle typing stop event."""
        await self.remove_typing_indicator()

        # Broadcast typing stopped to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'is_typing': False,
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name() or self.user.email,
            }
        )

    async def handle_read_receipt(self, content):
        """Handle read receipt event."""
        message_id = content.get('message_id')
        if not message_id:
            return

        # Mark message as read
        success = await self.mark_message_as_read(message_id)

        if success:
            # Broadcast read receipt to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': str(self.user.id),
                    'read_at': timezone.now().isoformat(),
                }
            )

    async def handle_delivery_receipt(self, content):
        """Handle delivery receipt event."""
        message_id = content.get('message_id')
        if not message_id:
            return

        # Mark message as delivered
        success = await self.mark_message_as_delivered(message_id)

        if success:
            # Broadcast delivery receipt to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delivery_receipt',
                    'message_id': message_id,
                    'user_id': str(self.user.id),
                    'delivered_at': timezone.now().isoformat(),
                }
            )

    # Event handlers for messages from channel layer

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send_json(event['message'])

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the user who is typing
        if event.get('user_id') != str(self.user.id):
            await self.send_json({
                'type': 'typing_indicator',
                'is_typing': event['is_typing'],
                'user_id': event['user_id'],
                'user_name': event['user_name'],
            })

    async def read_receipt(self, event):
        """Send read receipt to WebSocket."""
        await self.send_json({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'read_at': event['read_at'],
        })

    async def delivery_receipt(self, event):
        """Send delivery receipt to WebSocket."""
        await self.send_json({
            'type': 'delivery_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'delivered_at': event['delivered_at'],
        })

    async def user_joined(self, event):
        """Send user joined event to WebSocket."""
        # Don't send to the user who joined
        if event.get('user_id') != str(self.user.id):
            await self.send_json({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
            })

    async def user_left(self, event):
        """Send user left event to WebSocket."""
        # Don't send to the user who left
        if event.get('user_id') != str(self.user.id):
            await self.send_json({
                'type': 'user_left',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
            })

    # Database operations

    @database_sync_to_async
    def verify_room_access(self):
        """Verify user has access to chat room."""
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            if self.user == room.customer:
                return True
            if hasattr(room.partner, 'user') and self.user == room.partner.user:
                return True
            return False
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, message_type, metadata):
        """Save message to database."""
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)

            message = ChatMessage.objects.create(
                room=room,
                sender=self.user,
                message_type=message_type,
                content=content,
                metadata=metadata,
            )

            return message.to_websocket_message()
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def set_typing_indicator(self):
        """Set typing indicator for user in room."""
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            TypingIndicator.objects.update_or_create(
                room=room,
                user=self.user
            )
            return True
        except Exception as e:
            logger.error(f"Error setting typing indicator: {e}")
            return False

    @database_sync_to_async
    def remove_typing_indicator(self):
        """Remove typing indicator for user in room."""
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            TypingIndicator.objects.filter(
                room=room,
                user=self.user
            ).delete()
            return True
        except Exception as e:
            logger.error(f"Error removing typing indicator: {e}")
            return False

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark message as read."""
        try:
            message = ChatMessage.objects.get(id=message_id)
            # Only allow recipient to mark as read
            if message.get_recipient() == self.user:
                message.mark_as_read()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False

    @database_sync_to_async
    def mark_message_as_delivered(self, message_id):
        """Mark message as delivered."""
        try:
            message = ChatMessage.objects.get(id=message_id)
            # Only allow recipient to mark as delivered
            if message.get_recipient() == self.user:
                message.mark_as_delivered()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking message as delivered: {e}")
            return False
