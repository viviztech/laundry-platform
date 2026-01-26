# Phase 5: Notifications System - Implementation Plan

**Date**: 2026-01-02
**Phase**: 5 of 20-week implementation plan
**Status**: Planning

## Overview

Implement a comprehensive notification system with email notifications, in-app notifications, and real-time updates for order status, payments, and system events.

## Current Infrastructure (Already Available)

### ✅ Email Configuration
- **Development**: Console backend (prints to terminal)
- **Production**: SendGrid SMTP configured
- **Settings**: All email settings in `config/settings/production.py`

### ✅ Async Task Processing
- **Celery**: v5.3.4 installed and configured
- **Redis**: v5.0.1 configured as message broker
- **Timezone**: Asia/Kolkata (Indian timezone)

### ✅ User Notification Preferences
- `UserProfile.receive_notifications` - Global opt-in/out
- `UserProfile.receive_marketing_emails` - Marketing emails opt-in/out
- `UserProfile.preferred_language` - For localized emails

### ✅ Notification Trigger Points
**Orders**: 8 status changes (pending → delivered)
**Payments**: 4 events (initiated, completed, failed, refunded)
**Partners**: 3 events (assignment, approval, updates)
**Accounts**: 2 events (registration, verification)

## Implementation Strategy

### 1. Database Models

#### Notification Model
**Purpose**: Store all in-app notifications for users

```python
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_created', 'Order Created'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_picked_up', 'Order Picked Up'),
        ('order_in_progress', 'Order In Progress'),
        ('order_ready', 'Order Ready for Delivery'),
        ('order_out_for_delivery', 'Order Out for Delivery'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('refund_initiated', 'Refund Initiated'),
        ('refund_completed', 'Refund Completed'),
        ('partner_assigned', 'Partner Assigned'),
        ('partner_approved', 'Partner Approved'),
        ('account_verified', 'Account Verified'),
        ('general', 'General Notification'),
    ]

    id = UUIDField(primary_key=True)
    notification_id = CharField(unique=True)  # Format: NOTIF{YYYYMMDD}{8-char}
    user = ForeignKey(User)
    type = CharField(choices=NOTIFICATION_TYPES)
    title = CharField(max_length=255)
    message = TextField()

    # Related objects
    order = ForeignKey(Order, null=True, blank=True)
    payment = ForeignKey(Payment, null=True, blank=True)

    # Status
    is_read = BooleanField(default=False)
    read_at = DateTimeField(null=True, blank=True)

    # Delivery tracking
    email_sent = BooleanField(default=False)
    email_sent_at = DateTimeField(null=True, blank=True)

    # Metadata
    action_url = CharField(max_length=500, blank=True)  # Deep link
    metadata = JSONField(default=dict, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### NotificationTemplate Model
**Purpose**: Store customizable email templates

```python
class NotificationTemplate(models.Model):
    TEMPLATE_TYPES = [
        # Same as Notification.NOTIFICATION_TYPES
    ]

    type = CharField(choices=TEMPLATE_TYPES, unique=True)
    name = CharField(max_length=255)

    # Email template
    email_subject = CharField(max_length=255)
    email_body_html = TextField()  # HTML version
    email_body_text = TextField()  # Plain text version

    # In-app template
    title_template = CharField(max_length=255)  # Can use {{ variables }}
    message_template = TextField()

    # SMS template (future)
    sms_template = CharField(max_length=160, blank=True)

    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### NotificationPreference Model
**Purpose**: User-level preferences for different notification types

```python
class NotificationPreference(models.Model):
    user = OneToOneField(User, related_name='notification_preferences')

    # Order notifications
    order_updates_email = BooleanField(default=True)
    order_updates_push = BooleanField(default=True)

    # Payment notifications
    payment_updates_email = BooleanField(default=True)
    payment_updates_push = BooleanField(default=True)

    # Partner notifications (for partners only)
    partner_updates_email = BooleanField(default=True)
    partner_updates_push = BooleanField(default=True)

    # Marketing
    marketing_emails = BooleanField(default=False)
    promotional_push = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### 2. Email Templates

**Directory Structure**:
```
apps/notifications/templates/emails/
├── base.html                      # Base email template with header/footer
├── order/
│   ├── order_created.html
│   ├── order_confirmed.html
│   ├── order_picked_up.html
│   ├── order_in_progress.html
│   ├── order_ready.html
│   ├── order_out_for_delivery.html
│   ├── order_delivered.html
│   └── order_cancelled.html
├── payment/
│   ├── payment_completed.html
│   ├── payment_failed.html
│   ├── refund_initiated.html
│   └── refund_completed.html
├── partner/
│   ├── partner_assigned.html
│   ├── partner_approved.html
│   └── new_order_assignment.html
└── account/
    ├── welcome.html
    └── account_verified.html
```

### 3. Celery Tasks

**File**: `apps/notifications/tasks.py`

```python
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def send_notification_email(notification_id):
    """Send email for a notification asynchronously"""
    notification = Notification.objects.get(id=notification_id)

    # Check user preferences
    if not should_send_email(notification):
        return

    # Get template
    template = NotificationTemplate.objects.get(type=notification.type)

    # Render email
    context = build_email_context(notification)
    html_message = render_to_string(template.email_body_html, context)
    plain_message = render_to_string(template.email_body_text, context)

    # Send email
    send_mail(
        subject=template.email_subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[notification.user.email],
        html_message=html_message,
    )

    # Update notification
    notification.email_sent = True
    notification.email_sent_at = timezone.now()
    notification.save()

@shared_task
def send_bulk_notifications(user_ids, notification_type, context):
    """Send notifications to multiple users"""
    pass

@shared_task
def cleanup_old_notifications():
    """Delete read notifications older than 30 days"""
    pass
```

### 4. Signal Handlers

**File**: `apps/notifications/signals.py`

```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.orders.models import Order
from apps.payments.models import Payment, Refund

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Create notification when order status changes"""
    if created:
        create_notification(
            user=instance.user,
            type='order_created',
            order=instance,
        )
    elif instance._state.db and instance.status != instance._state.db['status']:
        # Status changed
        notification_type = f'order_{instance.status}'
        create_notification(
            user=instance.user,
            type=notification_type,
            order=instance,
        )

@receiver(post_save, sender=Payment)
def payment_status_changed(sender, instance, created, **kwargs):
    """Create notification when payment status changes"""
    if instance.status == 'completed':
        create_notification(
            user=instance.user,
            type='payment_completed',
            payment=instance,
        )
    elif instance.status == 'failed':
        create_notification(
            user=instance.user,
            type='payment_failed',
            payment=instance,
        )

def create_notification(user, type, **kwargs):
    """Create notification and trigger async email"""
    notification = Notification.objects.create(
        user=user,
        type=type,
        **kwargs
    )

    # Trigger async email
    send_notification_email.delay(notification.id)
```

### 5. API Endpoints

#### NotificationViewSet
```
GET /api/notifications/ - List user's notifications
GET /api/notifications/unread/ - Unread notifications count
POST /api/notifications/{id}/mark_read/ - Mark as read
POST /api/notifications/mark_all_read/ - Mark all as read
DELETE /api/notifications/{id}/ - Delete notification
```

#### NotificationPreferenceViewSet
```
GET /api/notifications/preferences/ - Get preferences
PUT /api/notifications/preferences/ - Update preferences
```

### 6. Real-time Updates (Future Enhancement)

**Options**:
1. **Django Channels** - WebSocket support
2. **Server-Sent Events (SSE)** - Simpler, one-way
3. **Polling** - Simple but less efficient

**Implementation**: Start with polling, migrate to SSE/WebSockets in Phase 6.

## Implementation Steps

### Step 1: Create Notifications App
- [x] Create `apps/notifications/` directory structure
- [ ] Add models (Notification, NotificationTemplate, NotificationPreference)
- [ ] Create migrations
- [ ] Add to INSTALLED_APPS

### Step 2: Admin Interface
- [ ] NotificationAdmin - View/manage notifications
- [ ] NotificationTemplateAdmin - Edit email templates
- [ ] NotificationPreferenceAdmin - Manage user preferences

### Step 3: Email Templates
- [ ] Create base email template with LaundryConnect branding
- [ ] Create templates for all notification types
- [ ] Add template variables and dynamic content

### Step 4: Celery Tasks
- [ ] Implement `send_notification_email` task
- [ ] Implement `send_bulk_notifications` task
- [ ] Add retry logic and error handling
- [ ] Test with Celery worker

### Step 5: Signal Handlers
- [ ] Create signals for Order status changes
- [ ] Create signals for Payment events
- [ ] Create signals for Partner events
- [ ] Connect signals in apps.py

### Step 6: API Endpoints
- [ ] NotificationSerializer
- [ ] NotificationViewSet with all actions
- [ ] NotificationPreferenceSerializer
- [ ] Add URLs

### Step 7: Default Templates
- [ ] Create seed data for NotificationTemplate
- [ ] Create management command to load default templates
- [ ] Write default HTML/text templates

### Step 8: Testing
- [ ] Unit tests for models
- [ ] Tests for Celery tasks
- [ ] API endpoint tests
- [ ] Integration tests for notification flow

### Step 9: Documentation
- [ ] Update README.md
- [ ] Create PHASE_5_SUMMARY.md
- [ ] Update API documentation
- [ ] Add notification testing guide

## Files to Create

1. `apps/notifications/__init__.py`
2. `apps/notifications/apps.py`
3. `apps/notifications/models.py`
4. `apps/notifications/admin.py`
5. `apps/notifications/serializers.py`
6. `apps/notifications/views.py`
7. `apps/notifications/urls.py`
8. `apps/notifications/tasks.py`
9. `apps/notifications/signals.py`
10. `apps/notifications/utils.py`
11. `apps/notifications/management/commands/load_notification_templates.py`
12. `apps/notifications/templates/emails/base.html`
13. `apps/notifications/templates/emails/*/[various].html`
14. `apps/notifications/tests.py`

## Files to Modify

1. `config/settings/base.py` - Add notifications to INSTALLED_APPS
2. `config/urls.py` - Add notifications URLs
3. `apps/orders/models.py` - Add signal connection
4. `apps/payments/models.py` - Add signal connection
5. `apps/partners/models.py` - Add signal connection

## Environment Variables Required

```bash
# Email (Production)
EMAIL_HOST_USER=your-sendgrid-username
EMAIL_HOST_PASSWORD=your-sendgrid-password
DEFAULT_FROM_EMAIL=noreply@laundryconnect.com
SENDGRID_API_KEY=your-sendgrid-api-key  # Optional

# Celery (Already configured)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Success Criteria

- [ ] Notifications created automatically on order status changes
- [ ] Emails sent asynchronously via Celery
- [ ] Users can view their notifications via API
- [ ] Users can mark notifications as read
- [ ] Users can customize notification preferences
- [ ] Email templates are customizable via admin
- [ ] All notification types have working email templates
- [ ] No blocking operations on main request/response cycle
- [ ] Admin can send bulk notifications
- [ ] Cleanup task removes old notifications

## Timeline

**Estimated Time**: 1 week (Phase 5)

**Breakdown**:
- Day 1: Models, migrations, admin (4 hours)
- Day 2: Email templates creation (4 hours)
- Day 3: Celery tasks and signals (4 hours)
- Day 4: API endpoints and serializers (4 hours)
- Day 5: Testing and documentation (4 hours)

## Future Enhancements (Phase 6+)

1. **Real-time Notifications**
   - Implement Django Channels
   - WebSocket support for live updates
   - Browser push notifications

2. **SMS Notifications**
   - Integrate Twilio/AWS SNS
   - SMS templates
   - SMS notification preferences

3. **Push Notifications (Mobile)**
   - FCM (Firebase Cloud Messaging)
   - APNs (Apple Push Notification service)
   - Device token management

4. **Advanced Features**
   - Notification scheduling
   - A/B testing for email templates
   - Email analytics (open rates, click rates)
   - Multi-language support
   - Rich notifications with images/buttons

---

**Next Step**: Start implementation with notification models
