"""
Chat models for LaundryConnect platform.

This module provides real-time messaging functionality between customers and partners.
"""

import uuid
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from apps.accounts.models import User
from apps.orders.models import Order
from apps.partners.models import Partner


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChatRoom(BaseModel):
    """
    Chat room for communication between customer and partner regarding an order.

    Each order gets one chat room where the customer and assigned partner can communicate.
    """

    room_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique identifier for the chat room (e.g., CHAT20260103ABC12345)"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='chat_room',
        help_text="Order associated with this chat room"
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_chat_rooms',
        help_text="Customer in this chat"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='partner_chat_rooms',
        help_text="Partner in this chat"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the chat room is active"
    )
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last message"
    )
    customer_unread_count = models.IntegerField(
        default=0,
        help_text="Number of unread messages for customer"
    )
    partner_unread_count = models.IntegerField(
        default=0,
        help_text="Number of unread messages for partner"
    )

    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-last_message_at', '-created_at']
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        indexes = [
            models.Index(fields=['customer', '-last_message_at']),
            models.Index(fields=['partner', '-last_message_at']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.room_id} - Order #{self.order.order_number}"

    def save(self, *args, **kwargs):
        """Generate room_id if not set."""
        if not self.room_id:
            self.room_id = self.generate_room_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_room_id():
        """Generate unique room ID in format: CHAT{YYYYMMDD}{8-char-random}"""
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = uuid.uuid4().hex[:8].upper()
        return f"CHAT{date_str}{random_str}"

    def increment_unread_count(self, for_user):
        """Increment unread count for a specific user."""
        if for_user == self.customer:
            self.customer_unread_count += 1
        elif for_user == self.partner.user:
            self.partner_unread_count += 1
        self.save(update_fields=['customer_unread_count', 'partner_unread_count'])

    def reset_unread_count(self, for_user):
        """Reset unread count for a specific user."""
        if for_user == self.customer:
            self.customer_unread_count = 0
            self.save(update_fields=['customer_unread_count'])
        elif for_user == self.partner.user:
            self.partner_unread_count = 0
            self.save(update_fields=['partner_unread_count'])

    def get_participant_ids(self):
        """Get list of participant user IDs."""
        return [str(self.customer.id), str(self.partner.user.id)]


class ChatMessage(BaseModel):
    """
    Individual message in a chat room.

    Supports various message types including text, images, files, and location sharing.
    """

    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File Attachment'),
        ('location', 'Location Share'),
        ('system', 'System Message'),
    ]

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Chat room this message belongs to"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text',
        help_text="Type of message"
    )
    content = models.TextField(
        help_text="Message content (text or file URL)"
    )
    file = models.FileField(
        upload_to='chat/files/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            )
        ],
        help_text="Uploaded file (for image/file messages)"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data (location coordinates, file info, etc.)"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the message has been read by recipient"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the message was read"
    )
    is_delivered = models.BooleanField(
        default=False,
        help_text="Whether the message was delivered to recipient"
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the message was delivered"
    )

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['room', 'is_read']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.email} in {self.room.room_id} - {self.message_type}"

    def save(self, *args, **kwargs):
        """Update room's last_message_at and unread counts."""
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            # Update room's last message timestamp
            self.room.last_message_at = self.created_at
            self.room.save(update_fields=['last_message_at'])

            # Increment unread count for recipient
            recipient = self.get_recipient()
            if recipient:
                self.room.increment_unread_count(recipient)

    def get_recipient(self):
        """Get the recipient of this message."""
        if self.sender == self.room.customer:
            return self.room.partner.user
        elif self.sender == self.room.partner.user:
            return self.room.customer
        return None

    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_delivered(self):
        """Mark message as delivered."""
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save(update_fields=['is_delivered', 'delivered_at'])

    def get_file_url(self):
        """Get full URL for uploaded file."""
        if self.file:
            return self.file.url
        return None

    def to_websocket_message(self):
        """Convert to WebSocket message format."""
        return {
            'id': str(self.id),
            'room_id': self.room.room_id,
            'sender_id': str(self.sender.id),
            'sender_name': self.sender.get_full_name() or self.sender.email,
            'message_type': self.message_type,
            'content': self.content,
            'file_url': self.get_file_url(),
            'metadata': self.metadata,
            'is_read': self.is_read,
            'is_delivered': self.is_delivered,
            'created_at': self.created_at.isoformat(),
        }


class TypingIndicator(models.Model):
    """
    Track who is currently typing in a chat room.

    Used for real-time typing indicators in the UI.
    """

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='typing_indicators'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='typing_in_rooms'
    )
    started_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_typing_indicators'
        unique_together = [['room', 'user']]
        verbose_name = 'Typing Indicator'
        verbose_name_plural = 'Typing Indicators'

    def __str__(self):
        return f"{self.user.email} typing in {self.room.room_id}"

    def is_expired(self, timeout=10):
        """Check if typing indicator has expired (default 10 seconds)."""
        if not self.started_at:
            return True
        time_diff = (timezone.now() - self.started_at).total_seconds()
        return time_diff > timeout
