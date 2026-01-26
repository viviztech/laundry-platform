"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    PushSubscription,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""

    list_display = (
        'notification_id', 'user', 'type', 'title_preview',
        'is_read', 'email_sent', 'created_at'
    )
    list_filter = (
        'is_read', 'email_sent', 'type', 'created_at'
    )
    search_fields = (
        'notification_id', 'user__email', 'user__first_name',
        'user__last_name', 'title', 'message'
    )
    readonly_fields = (
        'notification_id', 'read_at', 'email_sent_at',
        'created_at', 'updated_at'
    )
    ordering = ('-created_at',)

    fieldsets = (
        ('Notification Information', {
            'fields': (
                'notification_id', 'user', 'type', 'title', 'message'
            )
        }),
        ('Related Objects', {
            'fields': ('order', 'payment'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (
                'is_read', 'read_at', 'email_sent',
                'email_sent_at', 'email_error'
            )
        }),
        ('Action', {
            'fields': ('action_url', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    list_select_related = ('user', 'order', 'payment')

    actions = ['mark_as_read', 'mark_as_unread', 'resend_email']

    def title_preview(self, obj):
        """Show truncated title."""
        if len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title
    title_preview.short_description = 'Title'

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = 0
        for notification in queryset.filter(is_read=False):
            notification.mark_as_read()
            count += 1
        self.message_user(request, f'{count} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'

    def resend_email(self, request, queryset):
        """Resend email for selected notifications."""
        from .tasks import send_notification_email
        count = 0
        for notification in queryset:
            send_notification_email.delay(str(notification.id))
            count += 1
        self.message_user(request, f'Email resend queued for {count} notifications.')
    resend_email.short_description = 'Resend email'

    def has_add_permission(self, request):
        """Notifications are created automatically, not manually."""
        return False


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationTemplate model."""

    list_display = (
        'type', 'name', 'is_active', 'has_email',
        'has_sms', 'updated_at'
    )
    list_filter = ('is_active', 'type')
    search_fields = ('name', 'description', 'type')
    ordering = ('type',)

    fieldsets = (
        ('Template Information', {
            'fields': ('type', 'name', 'description', 'is_active')
        }),
        ('Email Template', {
            'fields': (
                'email_subject', 'email_body_html', 'email_body_text'
            ),
            'description': 'Use {{ variable_name }} for template variables'
        }),
        ('In-App Notification Template', {
            'fields': ('title_template', 'message_template')
        }),
        ('SMS Template (Future)', {
            'fields': ('sms_template',),
            'classes': ('collapse',)
        }),
        ('Action', {
            'fields': ('action_url_template',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def has_email(self, obj):
        """Check if email template is configured."""
        return bool(obj.email_subject and obj.email_body_html)
    has_email.boolean = True
    has_email.short_description = 'Email'

    def has_sms(self, obj):
        """Check if SMS template is configured."""
        return bool(obj.sms_template)
    has_sms.boolean = True
    has_sms.short_description = 'SMS'

    actions = ['activate_templates', 'deactivate_templates']

    def activate_templates(self, request, queryset):
        """Activate selected templates."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} templates activated.')
    activate_templates.short_description = 'Activate selected templates'

    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} templates deactivated.')
    deactivate_templates.short_description = 'Deactivate selected templates'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationPreference model."""

    list_display = (
        'user', 'email_status', 'push_status', 'marketing_status',
        'updated_at'
    )
    list_filter = (
        'order_updates_email', 'payment_updates_email',
        'marketing_emails', 'promotional_push'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name'
    )
    ordering = ('-updated_at',)

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Order Notifications', {
            'fields': (
                'order_updates_email', 'order_updates_push',
                'order_updates_sms'
            )
        }),
        ('Payment Notifications', {
            'fields': (
                'payment_updates_email', 'payment_updates_push',
                'payment_updates_sms'
            )
        }),
        ('Refund Notifications', {
            'fields': ('refund_updates_email', 'refund_updates_push')
        }),
        ('Partner Notifications', {
            'fields': ('partner_updates_email', 'partner_updates_push')
        }),
        ('Marketing & Promotions', {
            'fields': ('marketing_emails', 'promotional_push')
        }),
        ('Account Notifications', {
            'fields': ('account_updates_email',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)

    def email_status(self, obj):
        """Show email notification status with color."""
        enabled = (
            obj.order_updates_email or
            obj.payment_updates_email or
            obj.refund_updates_email
        )
        if enabled:
            return format_html(
                '<span style="color: green;">{}</span>', '✓ Enabled'
            )
        return format_html('<span style="color: red;">{}</span>', '✗ Disabled')
    email_status.short_description = 'Email Notifications'

    def push_status(self, obj):
        """Show push notification status with color."""
        enabled = (
            obj.order_updates_push or
            obj.payment_updates_push or
            obj.refund_updates_push
        )
        if enabled:
            return format_html(
                '<span style="color: green;">{}</span>', '✓ Enabled'
            )
        return format_html('<span style="color: red;">{}</span>', '✗ Disabled')
    push_status.short_description = 'Push Notifications'

    def marketing_status(self, obj):
        """Show marketing status."""
        if obj.marketing_emails or obj.promotional_push:
            return format_html(
                '<span style="color: orange;">{}</span>', '⚠ Opted In'
            )
        return format_html('<span style="color: gray;">{}</span>', '✗ Opted Out')
    marketing_status.short_description = 'Marketing'

    actions = ['enable_all_notifications', 'disable_marketing']

    def enable_all_notifications(self, request, queryset):
        """Enable all notification types for selected users."""
        count = queryset.update(
            order_updates_email=True,
            order_updates_push=True,
            payment_updates_email=True,
            payment_updates_push=True,
            refund_updates_email=True,
            refund_updates_push=True,
        )
        self.message_user(
            request,
            f'All notifications enabled for {count} users.'
        )
    enable_all_notifications.short_description = 'Enable all notifications'

    def disable_marketing(self, request, queryset):
        """Disable marketing for selected users."""
        count = queryset.update(
            marketing_emails=False,
            promotional_push=False
        )
        self.message_user(
            request,
            f'Marketing disabled for {count} users.'
        )
    disable_marketing.short_description = 'Disable marketing'


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for PushSubscription model."""

    list_display = (
        'user', 'device_name', 'is_active', 'created_at',
        'last_used_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'device_name', 'endpoint'
    )
    readonly_fields = (
        'id', 'endpoint', 'p256dh_key', 'auth_key',
        'created_at', 'updated_at', 'last_used_at'
    )
    ordering = ('-created_at',)

    fieldsets = (
        ('User & Device', {
            'fields': ('user', 'device_name', 'user_agent')
        }),
        ('Subscription Details', {
            'fields': ('endpoint', 'p256dh_key', 'auth_key'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',)
        }),
    )

    list_select_related = ('user',)

    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'test_push']

    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'

    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'

    def test_push(self, request, queryset):
        """Send test push notification to selected subscriptions."""
        from .push import push_service
        from django.utils import timezone

        count = 0
        for subscription in queryset.filter(is_active=True):
            notification_data = {
                'title': 'Test Push Notification',
                'body': 'This is a test notification from LaundryConnect Admin',
                'icon': '/static/images/logo-192x192.png',
                'data': {'url': '/', 'test': True}
            }

            result = push_service.send_push_notification(
                subscription.get_subscription_info(),
                notification_data
            )

            if result['success']:
                subscription.last_used_at = timezone.now()
                subscription.save(update_fields=['last_used_at'])
                count += 1

        self.message_user(request, f'Test push sent to {count} subscriptions.')
    test_push.short_description = 'Send test push notification'

    def has_add_permission(self, request):
        """Push subscriptions are created by browsers, not manually."""
        return False
