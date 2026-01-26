"""
REST API views for Chat functionality.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import ChatRoom, ChatMessage, TypingIndicator
from .serializers import (
    ChatRoomSerializer,
    ChatRoomCreateSerializer,
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    TypingIndicatorSerializer,
    MarkMessagesReadSerializer,
)
from apps.notifications.utils import create_notification


class ChatMessagePagination(PageNumberPagination):
    """Pagination for chat messages."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat rooms.

    Endpoints:
    - GET /chat/rooms/ - List user's chat rooms
    - POST /chat/rooms/ - Create chat room for an order
    - GET /chat/rooms/{id}/ - Get chat room details
    - GET /chat/rooms/{id}/messages/ - Get messages in room
    - POST /chat/rooms/{id}/mark_read/ - Mark messages as read
    """

    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'room_id'

    def get_queryset(self):
        """Get chat rooms for current user (as customer or partner)."""
        user = self.request.user

        # Check if user is a partner
        try:
            from apps.partners.models import Partner
            partner = Partner.objects.get(user=user)
            # User is a partner - show their partner chat rooms
            return ChatRoom.objects.filter(
                Q(partner=partner) | Q(customer=user)
            ).select_related('customer', 'partner', 'order').prefetch_related('messages')
        except Partner.DoesNotExist:
            # User is a customer - show their customer chat rooms
            return ChatRoom.objects.filter(
                customer=user
            ).select_related('customer', 'partner', 'order').prefetch_related('messages')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def create(self, request, *args, **kwargs):
        """Create a new chat room for an order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_room = serializer.save()

        # Return the created chat room
        response_serializer = ChatRoomSerializer(chat_room, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, room_id=None):
        """Get all messages in a chat room with pagination."""
        chat_room = self.get_object()

        # Verify user has access to this room
        if not self._user_has_room_access(request.user, chat_room):
            return Response(
                {'error': 'You do not have access to this chat room.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get messages with pagination
        messages = chat_room.messages.select_related('sender').order_by('created_at')

        # Apply pagination
        paginator = ChatMessagePagination()
        page = paginator.paginate_queryset(messages, request)

        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, room_id=None):
        """Mark messages as read in a chat room."""
        chat_room = self.get_object()

        # Verify user has access to this room
        if not self._user_has_room_access(request.user, chat_room):
            return Response(
                {'error': 'You do not have access to this chat room.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MarkMessagesReadSerializer(
            data=request.data,
            context={'room_id': room_id}
        )
        serializer.is_valid(raise_exception=True)

        message_ids = serializer.validated_data.get('message_ids')

        if message_ids:
            # Mark specific messages as read
            messages = ChatMessage.objects.filter(
                id__in=message_ids,
                room=chat_room
            ).exclude(sender=request.user)
        else:
            # Mark all unread messages as read
            messages = ChatMessage.objects.filter(
                room=chat_room,
                is_read=False
            ).exclude(sender=request.user)

        # Mark messages as read
        count = 0
        for message in messages:
            message.mark_as_read()
            count += 1

        # Reset unread count for user
        chat_room.reset_unread_count(request.user)

        return Response({
            'message': f'{count} message(s) marked as read.',
            'marked_count': count
        })

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, room_id=None):
        """Send a message in a chat room (alternative to WebSocket)."""
        chat_room = self.get_object()

        # Verify user has access to this room
        if not self._user_has_room_access(request.user, chat_room):
            return Response(
                {'error': 'You do not have access to this chat room.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create message
        data = request.data.copy()
        data['room'] = chat_room.id

        serializer = ChatMessageCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Send notification to recipient
        recipient = message.get_recipient()
        if recipient:
            create_notification(
                user=recipient,
                notification_type='chat_message',
                title='New Message',
                message=f'New message in chat for order #{chat_room.order.order_number}',
                metadata={
                    'room_id': chat_room.room_id,
                    'message_id': str(message.id),
                    'sender_name': request.user.get_full_name() or request.user.email,
                }
            )

        # Return created message
        response_serializer = ChatMessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """Get total unread message count for current user."""
        user = request.user
        total_unread = 0

        try:
            from apps.partners.models import Partner
            partner = Partner.objects.get(user=user)
            # Sum partner unread counts
            rooms = ChatRoom.objects.filter(partner=partner)
            total_unread = sum(room.partner_unread_count for room in rooms)
        except Partner.DoesNotExist:
            # Sum customer unread counts
            rooms = ChatRoom.objects.filter(customer=user)
            total_unread = sum(room.customer_unread_count for room in rooms)

        return Response({
            'total_unread': total_unread,
            'room_count': rooms.count()
        })

    def _user_has_room_access(self, user, chat_room):
        """Check if user has access to the chat room."""
        if user == chat_room.customer:
            return True
        if hasattr(chat_room.partner, 'user') and user == chat_room.partner.user:
            return True
        return False


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages.

    Endpoints:
    - GET /chat/messages/ - List user's recent messages
    - POST /chat/messages/ - Send a message
    - GET /chat/messages/{id}/ - Get message details
    - POST /chat/messages/{id}/mark-read/ - Mark message as read
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatMessagePagination

    def get_queryset(self):
        """Get messages for current user's chat rooms."""
        user = self.request.user

        # Get all chat rooms user has access to
        try:
            from apps.partners.models import Partner
            partner = Partner.objects.get(user=user)
            room_ids = ChatRoom.objects.filter(
                Q(partner=partner) | Q(customer=user)
            ).values_list('id', flat=True)
        except Partner.DoesNotExist:
            room_ids = ChatRoom.objects.filter(
                customer=user
            ).values_list('id', flat=True)

        # Get messages from those rooms
        return ChatMessage.objects.filter(
            room_id__in=room_ids
        ).select_related('room', 'sender').order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer

    def create(self, request, *args, **kwargs):
        """Create a new message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Send notification to recipient
        recipient = message.get_recipient()
        if recipient:
            create_notification(
                user=recipient,
                notification_type='chat_message',
                title='New Message',
                message=f'New message from {request.user.get_full_name() or request.user.email}',
                metadata={
                    'room_id': message.room.room_id,
                    'message_id': str(message.id),
                }
            )

        # Return created message
        response_serializer = ChatMessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a specific message as read."""
        message = self.get_object()

        # Only recipient can mark as read
        if message.sender == request.user:
            return Response(
                {'error': 'You cannot mark your own message as read.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify user is recipient
        recipient = message.get_recipient()
        if recipient != request.user:
            return Response(
                {'error': 'You do not have permission to mark this message as read.'},
                status=status.HTTP_403_FORBIDDEN
            )

        message.mark_as_read()

        return Response({
            'message': 'Message marked as read.',
            'read_at': message.read_at
        })


class TypingIndicatorViewSet(viewsets.ViewSet):
    """
    ViewSet for managing typing indicators.

    Endpoints:
    - POST /chat/typing/ - Start typing indicator
    - DELETE /chat/typing/ - Stop typing indicator
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        """Start typing indicator for a room."""
        room_id = request.data.get('room_id')

        if not room_id:
            return Response(
                {'error': 'room_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat_room = get_object_or_404(ChatRoom, room_id=room_id)

        # Verify user has access to this room
        if not self._user_has_room_access(request.user, chat_room):
            return Response(
                {'error': 'You do not have access to this chat room.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create or update typing indicator
        indicator, created = TypingIndicator.objects.update_or_create(
            room=chat_room,
            user=request.user
        )

        serializer = TypingIndicatorSerializer(indicator)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='stop')
    def stop(self, request):
        """Stop typing indicator for a room."""
        room_id = request.data.get('room_id')

        if not room_id:
            return Response(
                {'error': 'room_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat_room = get_object_or_404(ChatRoom, room_id=room_id)

        # Delete typing indicator
        TypingIndicator.objects.filter(
            room=chat_room,
            user=request.user
        ).delete()

        return Response({'message': 'Typing indicator stopped.'})

    def _user_has_room_access(self, user, chat_room):
        """Check if user has access to the chat room."""
        if user == chat_room.customer:
            return True
        if hasattr(chat_room.partner, 'user') and user == chat_room.partner.user:
            return True
        return False
