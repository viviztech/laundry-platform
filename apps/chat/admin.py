"""
Django admin configuration for Chat models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import ChatRoom, ChatMessage, TypingIndicator


class ChatMessageInline(admin.TabularInline):
    """Inline admin for ChatMessages in ChatRoom."""
    model = ChatMessage
    extra = 0
    fields = ['sender', 'message_type', 'content', 'is_read', 'is_delivered', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """Disable adding messages through admin inline."""
        return False


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """Admin interface for ChatRoom model."""

    list_display = [
        'room_id',
        'order_link',
        'customer_link',
        'partner_link',
        'message_count',
        'unread_status',
        'is_active',
        'last_message_at',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'created_at',
        'last_message_at',
    ]
    search_fields = [
        'room_id',
        'order__order_number',
        'customer__email',
        'customer__first_name',
        'customer__last_name',
        'partner__business_name',
    ]
    readonly_fields = [
        'id',
        'room_id',
        'created_at',
        'updated_at',
        'last_message_at',
        'customer_unread_count',
        'partner_unread_count',
    ]
    fieldsets = [
        ('Room Information', {
            'fields': ['id', 'room_id', 'order', 'is_active']
        }),
        ('Participants', {
            'fields': ['customer', 'partner']
        }),
        ('Status', {
            'fields': [
                'last_message_at',
                'customer_unread_count',
                'partner_unread_count',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    inlines = [ChatMessageInline]
    date_hierarchy = 'created_at'

    def order_link(self, obj):
        """Link to related order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def customer_link(self, obj):
        """Link to customer user."""
        url = reverse('admin:accounts_user_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.email)
    customer_link.short_description = 'Customer'

    def partner_link(self, obj):
        """Link to partner."""
        url = reverse('admin:partners_partner_change', args=[obj.partner.id])
        return format_html('<a href="{}">{}</a>', url, obj.partner.business_name)
    partner_link.short_description = 'Partner'

    def message_count(self, obj):
        """Total message count."""
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def unread_status(self, obj):
        """Display unread counts."""
        return format_html(
            'Customer: {} | Partner: {}',
            obj.customer_unread_count,
            obj.partner_unread_count
        )
    unread_status.short_description = 'Unread'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'customer', 'partner')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""

    list_display = [
        'id',
        'room_link',
        'sender_link',
        'message_type',
        'content_preview',
        'status_badges',
        'created_at',
    ]
    list_filter = [
        'message_type',
        'is_read',
        'is_delivered',
        'created_at',
    ]
    search_fields = [
        'content',
        'sender__email',
        'room__room_id',
        'room__order__order_number',
    ]
    readonly_fields = [
        'id',
        'room',
        'sender',
        'created_at',
        'updated_at',
        'read_at',
        'delivered_at',
        'file_preview',
    ]
    fieldsets = [
        ('Message Information', {
            'fields': ['id', 'room', 'sender', 'message_type']
        }),
        ('Content', {
            'fields': ['content', 'file', 'file_preview', 'metadata']
        }),
        ('Status', {
            'fields': [
                'is_delivered',
                'delivered_at',
                'is_read',
                'read_at',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'created_at'

    def room_link(self, obj):
        """Link to chat room."""
        url = reverse('admin:chat_chatroom_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room.room_id)
    room_link.short_description = 'Room'

    def sender_link(self, obj):
        """Link to sender user."""
        url = reverse('admin:accounts_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.email)
    sender_link.short_description = 'Sender'

    def content_preview(self, obj):
        """Preview of message content."""
        if obj.message_type == 'text':
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        elif obj.message_type in ['image', 'file']:
            return format_html('<i>{} attached</i>', obj.message_type.capitalize())
        elif obj.message_type == 'location':
            return '<i>Location shared</i>'
        return '<i>System message</i>'
    content_preview.short_description = 'Content'

    def status_badges(self, obj):
        """Display status badges."""
        badges = []
        if obj.is_delivered:
            badges.append('<span style="color: green;">✓ Delivered</span>')
        if obj.is_read:
            badges.append('<span style="color: blue;">✓✓ Read</span>')
        return mark_safe(' '.join(badges)) if badges else '<span style="color: gray;">Pending</span>'
    status_badges.short_description = 'Status'

    def file_preview(self, obj):
        """Preview uploaded file."""
        if obj.file:
            if obj.message_type == 'image':
                return format_html(
                    '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">Download File</a>',
                    obj.file.url
                )
        return '-'
    file_preview.short_description = 'File Preview'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('room', 'sender')

    def has_add_permission(self, request):
        """Disable adding messages through admin."""
        return False


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    """Admin interface for TypingIndicator model."""

    list_display = [
        'room_link',
        'user_link',
        'started_at',
        'is_active',
    ]
    list_filter = [
        'started_at',
    ]
    search_fields = [
        'user__email',
        'room__room_id',
    ]
    readonly_fields = ['room', 'user', 'started_at']

    def room_link(self, obj):
        """Link to chat room."""
        url = reverse('admin:chat_chatroom_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room.room_id)
    room_link.short_description = 'Room'

    def user_link(self, obj):
        """Link to user."""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'

    def is_active(self, obj):
        """Check if typing indicator is still active."""
        return not obj.is_expired()
    is_active.boolean = True
    is_active.short_description = 'Active'

    def has_add_permission(self, request):
        """Disable adding typing indicators through admin."""
        return False
