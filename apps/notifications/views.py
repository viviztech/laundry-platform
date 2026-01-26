"""
API views for notifications app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Notification, NotificationTemplate, NotificationPreference, PushSubscription
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationTemplateSerializer,
    NotificationPreferenceSerializer,
    MarkNotificationReadSerializer,
    BulkNotificationSerializer,
    PushSubscriptionSerializer,
    PushSubscriptionInputSerializer,
)
from .utils import get_unread_count, mark_all_as_read


@extend_schema_view(
    list=extend_schema(
        summary='List notifications',
        description='Get list of notifications for the authenticated user',
        parameters=[
            OpenApiParameter(name='is_read', description='Filter by read status', type=bool),
            OpenApiParameter(name='type', description='Filter by notification type'),
        ],
    ),
    retrieve=extend_schema(
        summary='Get notification details',
        description='Get detailed information about a specific notification',
    ),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications.
    Provides read-only access to notifications with actions for marking as read/unread.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Get notifications for current user."""
        queryset = Notification.objects.filter(
            user=self.request.user
        ).select_related('order', 'payment')

        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_read=is_read)

        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)

        return queryset

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    @extend_schema(
        summary='Get unread count',
        description='Get count of unread notifications for the authenticated user',
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}},
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = get_unread_count(request.user)
        return Response({'count': count})

    @extend_schema(
        summary='Mark notification as read',
        description='Mark a specific notification as read',
        request=MarkNotificationReadSerializer,
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        summary='Mark notification as unread',
        description='Mark a specific notification as unread',
    )
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """Mark notification as unread."""
        notification = self.get_object()
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=['is_read', 'read_at'])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        summary='Mark all as read',
        description='Mark all notifications as read for the authenticated user',
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}},
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = mark_all_as_read(request.user)
        return Response({'count': count, 'message': f'{count} notifications marked as read'})

    @extend_schema(
        summary='Delete notification',
        description='Delete a specific notification',
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a notification."""
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary='List notification templates',
        description='Get list of all notification templates (admin only)',
    ),
    retrieve=extend_schema(
        summary='Get template details',
        description='Get detailed information about a specific template (admin only)',
    ),
    create=extend_schema(
        summary='Create notification template',
        description='Create a new notification template (admin only)',
    ),
    update=extend_schema(
        summary='Update notification template',
        description='Update an existing notification template (admin only)',
    ),
    partial_update=extend_schema(
        summary='Partially update notification template',
        description='Partially update an existing notification template (admin only)',
    ),
    destroy=extend_schema(
        summary='Delete notification template',
        description='Delete a notification template (admin only)',
    ),
)
class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notification templates.
    Admin-only access for managing email and notification templates.
    """

    permission_classes = [IsAdminUser]
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer

    @extend_schema(
        summary='Activate template',
        description='Activate a notification template',
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a template."""
        template = self.get_object()
        template.is_active = True
        template.save(update_fields=['is_active'])
        serializer = self.get_serializer(template)
        return Response(serializer.data)

    @extend_schema(
        summary='Deactivate template',
        description='Deactivate a notification template',
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a template."""
        template = self.get_object()
        template.is_active = False
        template.save(update_fields=['is_active'])
        serializer = self.get_serializer(template)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary='Get notification preferences',
        description='Get notification preferences for the authenticated user',
    ),
    update=extend_schema(
        summary='Update notification preferences',
        description='Update notification preferences for the authenticated user',
    ),
    partial_update=extend_schema(
        summary='Partially update notification preferences',
        description='Partially update notification preferences',
    ),
)
class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notification preferences.
    Users can view and update their own notification preferences.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        """Get preferences for current user only."""
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create preferences for current user."""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences

    @extend_schema(
        summary='Get my preferences',
        description='Get notification preferences for the authenticated user',
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's notification preferences."""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """Return single preferences object instead of list."""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update preferences."""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Partially update preferences."""
        preferences = self.get_object()
        serializer = self.get_serializer(
            preferences,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema_view(
    create=extend_schema(
        summary='Send bulk notifications',
        description='Send notifications to multiple users (admin only)',
        request=BulkNotificationSerializer,
    ),
)
class BulkNotificationViewSet(viewsets.ViewSet):
    """
    ViewSet for sending bulk notifications.
    Admin-only access.
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary='Send bulk notifications',
        description='Queue bulk notifications to be sent to multiple users',
        request=BulkNotificationSerializer,
        responses={202: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
    )
    def create(self, request):
        """Send bulk notifications."""
        serializer = BulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data['user_ids']
        notification_type = serializer.validated_data['notification_type']
        context_data = serializer.validated_data.get('context_data', {})

        # Queue bulk notification task
        from .tasks import send_bulk_notifications
        send_bulk_notifications.delay(
            [str(uid) for uid in user_ids],
            notification_type,
            context_data
        )

        return Response(
            {
                'message': f'Bulk notifications queued for {len(user_ids)} users',
                'notification_type': notification_type
            },
            status=status.HTTP_202_ACCEPTED
        )


@extend_schema_view(
    list=extend_schema(
        summary='List push subscriptions',
        description='Get all active push subscriptions for the authenticated user',
    ),
    create=extend_schema(
        summary='Subscribe to push notifications',
        description='Create or update a push subscription for the authenticated user',
        request=PushSubscriptionInputSerializer,
    ),
    destroy=extend_schema(
        summary='Unsubscribe from push notifications',
        description='Delete a push subscription',
    ),
)
class PushSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing push notification subscriptions."""

    permission_classes = [IsAuthenticated]
    serializer_class = PushSubscriptionSerializer

    def get_queryset(self):
        """Return subscriptions for the authenticated user."""
        return PushSubscription.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        """Use different serializer for create action."""
        if self.action == 'create':
            return PushSubscriptionInputSerializer
        return PushSubscriptionSerializer

    def perform_destroy(self, instance):
        """Mark subscription as inactive instead of deleting."""
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @extend_schema(
        summary='Get VAPID public key',
        description='Get the VAPID public key for push notifications',
        responses={200: {'type': 'object', 'properties': {'public_key': {'type': 'string'}}}},
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def vapid_public_key(self, request):
        """Get VAPID public key for push subscription."""
        from django.conf import settings
        public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')

        if not public_key:
            return Response(
                {'error': 'VAPID public key not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({'public_key': public_key})
