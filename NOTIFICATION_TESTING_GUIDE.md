# LaundryConnect - Notification System Testing Guide

**Last Updated**: 2026-01-02
**Phase**: 5 - Notifications System

## Overview

This guide provides comprehensive instructions for testing the LaundryConnect notification system, including in-app notifications, email notifications, and the Celery async task system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Testing Email Templates](#testing-email-templates)
4. [Testing Notification Creation](#testing-notification-creation)
5. [Testing Celery Tasks](#testing-celery-tasks)
6. [Testing API Endpoints](#testing-api-endpoints)
7. [Testing Signal Handlers](#testing-signal-handlers)
8. [End-to-End Testing](#end-to-end-testing)
9. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

### Required Services
- **PostgreSQL**: Database running
- **Redis**: Message broker for Celery (port 6379)
- **Django**: Development server running
- **Celery Worker**: Background task processor

### Environment Variables
```bash
# Email Configuration (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For Production Testing
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-sendgrid-username
EMAIL_HOST_PASSWORD=your-sendgrid-password
DEFAULT_FROM_EMAIL=noreply@laundryconnect.com

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## Setup Instructions

### 1. Run Migrations

```bash
cd /Users/ganeshthangavel/projects/laundry-platform

# Activate virtual environment
source venv/bin/activate  # or your venv path

# Run migrations
python manage.py migrate
```

### 2. Load Default Notification Templates

```bash
# Load the 21 default notification templates
python manage.py load_notification_templates

# Verify templates were loaded
python manage.py shell
>>> from apps.notifications.models import NotificationTemplate
>>> NotificationTemplate.objects.count()
21  # Should show 21 templates
>>> exit()
```

### 3. Start Redis Server

```bash
# macOS (via Homebrew)
brew services start redis

# Or start manually
redis-server

# Verify Redis is running
redis-cli ping
# Should respond: PONG
```

### 4. Start Celery Worker

```bash
# In a new terminal window
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate

# Start Celery worker
celery -A config worker --loglevel=info

# You should see:
# [tasks]
#   . apps.notifications.tasks.cleanup_old_notifications
#   . apps.notifications.tasks.send_bulk_notifications
#   . apps.notifications.tasks.send_daily_summary_email
#   . apps.notifications.tasks.send_notification_email
```

### 5. Start Django Development Server

```bash
# In another terminal
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate
python manage.py runserver
```

---

## Testing Email Templates

### Visual Template Testing

1. **Create Test HTML File**

```bash
# Navigate to templates directory
cd apps/notifications/templates/emails/order

# Open any template in browser
open order_created.html  # macOS
# or
xdg-open order_created.html  # Linux
```

2. **Django Template Testing**

```python
# Django shell
python manage.py shell

from django.template.loader import render_to_string
from apps.accounts.models import User
from apps.orders.models import Order

# Get test data
user = User.objects.first()
order = Order.objects.first()

# Test rendering
context = {
    'user': user,
    'order': order,
    'action_url': 'https://app.laundryconnect.com/orders/' + str(order.id)
}

html = render_to_string('emails/order/order_created.html', context)
print(html)
```

### All Available Templates

| Category | Template File | Notification Type |
|----------|--------------|-------------------|
| **Order** | order_created.html | order_created |
| | order_confirmed.html | order_confirmed |
| | order_picked_up.html | order_picked_up |
| | order_in_progress.html | order_in_progress |
| | order_ready.html | order_ready |
| | order_out_for_delivery.html | order_out_for_delivery |
| | order_delivered.html | order_delivered |
| | order_cancelled.html | order_cancelled |
| **Payment** | payment_completed.html | payment_completed |
| | payment_failed.html | payment_failed |
| | refund_requested.html | refund_requested |
| | refund_processing.html | refund_processing |
| | refund_completed.html | refund_completed |
| | refund_failed.html | refund_failed |
| **Partner** | partner_assigned.html | partner_assigned |
| | partner_approved.html | partner_approved |
| | new_order_assigned.html | new_order_assigned |
| **Account** | welcome.html | welcome |
| | account_verified.html | account_verified |
| | password_changed.html | password_changed |
| **General** | general.html | general |
| | promotion.html | promotion |

---

## Testing Notification Creation

### Using Django Shell

```python
python manage.py shell

from apps.notifications.utils import create_notification
from apps.accounts.models import User
from apps.orders.models import Order

# Get test user and order
user = User.objects.first()
order = Order.objects.first()

# Test 1: Create order notification
notification = create_notification(
    user=user,
    notification_type='order_created',
    order=order
)

print(f"Created: {notification.notification_id}")
print(f"Title: {notification.title}")
print(f"Message: {notification.message}")
print(f"Email Sent: {notification.email_sent}")

# Test 2: Create payment notification
from apps.payments.models import Payment
payment = Payment.objects.first()

notification = create_notification(
    user=user,
    notification_type='payment_completed',
    payment=payment
)

# Test 3: Create general notification
notification = create_notification(
    user=user,
    notification_type='general',
    context_data={
        'title': 'System Maintenance',
        'message': 'Scheduled maintenance on Sunday'
    }
)

# Test 4: Create promotion notification
notification = create_notification(
    user=user,
    notification_type='promotion',
    context_data={
        'promo_title': 'Weekend Special',
        'promo_discount': '30% OFF',
        'promo_code': 'WEEKEND30'
    }
)
```

### Verify Notification in Database

```python
from apps.notifications.models import Notification

# Check latest notifications
notifications = Notification.objects.all().order_by('-created_at')[:5]
for notif in notifications:
    print(f"{notif.notification_id} - {notif.type} - {notif.is_read}")

# Check user notifications
user_notifs = Notification.objects.filter(user=user)
print(f"User has {user_notifs.count()} notifications")

# Check unread count
from apps.notifications.utils import get_unread_count
unread = get_unread_count(user)
print(f"Unread: {unread}")
```

---

## Testing Celery Tasks

### Test Email Sending Task

```python
python manage.py shell

from apps.notifications.tasks import send_notification_email
from apps.notifications.models import Notification

# Get a notification
notification = Notification.objects.filter(email_sent=False).first()

# Test 1: Send synchronously (for testing)
result = send_notification_email(str(notification.id))
print(f"Email sent: {result}")

# Refresh from database
notification.refresh_from_db()
print(f"Email sent status: {notification.email_sent}")
print(f"Sent at: {notification.email_sent_at}")

# Test 2: Queue with Celery (async)
task = send_notification_email.delay(str(notification.id))
print(f"Task ID: {task.id}")
print(f"Task Status: {task.status}")

# Check task result
result = task.get(timeout=10)
print(f"Result: {result}")
```

### Test Bulk Notification Task

```python
from apps.notifications.tasks import send_bulk_notifications
from apps.accounts.models import User

# Get multiple users
user_ids = list(User.objects.values_list('id', flat=True)[:5])

# Send bulk notification
context = {
    'promo_title': 'Flash Sale',
    'promo_discount': '50% OFF',
    'promo_code': 'FLASH50',
    'promo_validity': '2026-01-05'
}

task = send_bulk_notifications.delay(
    user_ids=[str(uid) for uid in user_ids],
    notification_type='promotion',
    context_data=context
)

print(f"Bulk task ID: {task.id}")
result = task.get(timeout=30)
print(f"Created {result} notifications")
```

### Monitor Celery Tasks

```bash
# In Celery worker terminal, you should see:
[2026-01-02 12:00:00,000: INFO/MainProcess] Received task: apps.notifications.tasks.send_notification_email[...]
[2026-01-02 12:00:01,000: INFO/ForkPoolWorker-1] Task apps.notifications.tasks.send_notification_email[...] succeeded in 1.234s: True
```

---

## Testing API Endpoints

### Setup for API Testing

```bash
# Get authentication token
python manage.py shell

from apps.accounts.models import User
from rest_framework.authtoken.models import Token

user = User.objects.first()
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
```

### Using cURL

#### 1. List Notifications

```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### 2. Get Unread Count

```bash
curl -X GET http://localhost:8000/api/notifications/unread_count/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### 3. Mark as Read

```bash
curl -X POST http://localhost:8000/api/notifications/{notification_id}/mark_read/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### 4. Mark All as Read

```bash
curl -X POST http://localhost:8000/api/notifications/mark_all_read/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### 5. Get Notification Preferences

```bash
curl -X GET http://localhost:8000/api/notifications/preferences/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### 6. Update Preferences

```bash
curl -X PUT http://localhost:8000/api/notifications/preferences/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "order_updates_email": true,
    "payment_updates_email": true,
    "marketing_emails": false
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = 'http://localhost:8000/api/notifications/'
TOKEN = 'your-token-here'
HEADERS = {'Authorization': f'Token {TOKEN}'}

# List notifications
response = requests.get(BASE_URL, headers=HEADERS)
print(response.json())

# Get unread count
response = requests.get(f'{BASE_URL}unread_count/', headers=HEADERS)
print(f"Unread: {response.json()['count']}")

# Mark notification as read
notif_id = 'notification-uuid'
response = requests.post(
    f'{BASE_URL}{notif_id}/mark_read/',
    headers=HEADERS
)
print(response.json())

# Update preferences
response = requests.put(
    f'{BASE_URL}preferences/me/',
    headers=HEADERS,
    json={
        'order_updates_email': True,
        'payment_updates_email': True,
        'refund_updates_email': True,
        'marketing_emails': False
    }
)
print(response.json())
```

---

## Testing Signal Handlers

### Test Order Signals

```python
python manage.py shell

from apps.orders.models import Order
from apps.notifications.models import Notification

# Get an order
order = Order.objects.first()
initial_count = Notification.objects.count()

# Update order status (triggers signal)
order.status = 'confirmed'
order.save()

# Check if notification was created
new_count = Notification.objects.count()
print(f"Notifications created: {new_count - initial_count}")

# Get the notification
notif = Notification.objects.filter(
    order=order,
    type='order_confirmed'
).first()
print(f"Notification: {notif.title}")

# Test other status changes
order.status = 'picked_up'
order.save()

order.status = 'in_progress'
order.save()

order.status = 'delivered'
order.save()

# Check all notifications for this order
order_notifs = Notification.objects.filter(order=order)
print(f"Total notifications for order: {order_notifs.count()}")
```

### Test Payment Signals

```python
from apps.payments.models import Payment
from apps.notifications.models import Notification

payment = Payment.objects.first()

# Update payment status
payment.status = 'completed'
payment.save()

# Check notification
notif = Notification.objects.filter(
    payment=payment,
    type='payment_completed'
).latest('created_at')
print(f"Payment notification: {notif.title}")
```

---

## End-to-End Testing

### Complete Order Flow Test

```python
python manage.py shell

from apps.accounts.models import User
from apps.orders.models import Order, OrderItem
from apps.services.models import Service
from apps.addresses.models import Address
from apps.notifications.models import Notification

# 1. Get or create test user
user = User.objects.first()
print(f"Testing with user: {user.email}")

# 2. Create order (triggers order_created notification)
address = Address.objects.filter(user=user).first()
order = Order.objects.create(
    user=user,
    address=address,
    pickup_date='2026-01-05',
    pickup_time_slot='10:00 AM - 12:00 PM',
    delivery_date='2026-01-07',
    delivery_time_slot='2:00 PM - 4:00 PM',
    total_amount=500.00,
    status='pending'
)

# Check notification
notif = Notification.objects.filter(order=order).latest('created_at')
print(f"✓ Order created notification: {notif.title}")

# 3. Confirm order
order.status = 'confirmed'
order.save()
notif = Notification.objects.filter(
    order=order,
    type='order_confirmed'
).first()
print(f"✓ Order confirmed notification: {notif.title}")

# 4. Pickup
order.status = 'picked_up'
order.save()
print("✓ Pickup notification sent")

# 5. Processing
order.status = 'in_progress'
order.save()
print("✓ Processing notification sent")

# 6. Ready
order.status = 'ready'
order.save()
print("✓ Ready notification sent")

# 7. Out for delivery
order.status = 'out_for_delivery'
order.save()
print("✓ Out for delivery notification sent")

# 8. Delivered
order.status = 'delivered'
order.save()
print("✓ Delivered notification sent")

# 9. Check all notifications
total_notifs = Notification.objects.filter(order=order).count()
print(f"\nTotal notifications created: {total_notifs}")

# 10. Check email status
email_sent_count = Notification.objects.filter(
    order=order,
    email_sent=True
).count()
print(f"Emails sent: {email_sent_count}/{total_notifs}")
```

### Check Email Output (Console Backend)

If using console email backend, check the Django runserver terminal for email output:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Order Confirmation - LaundryConnect
From: noreply@laundryconnect.com
To: user@example.com
Date: Thu, 02 Jan 2026 12:00:00 -0000

[Email content here]
```

---

## Common Issues & Solutions

### Issue 1: Celery Worker Not Starting

**Symptoms**: `celery -A config worker` fails

**Solution**:
```bash
# Check Redis is running
redis-cli ping

# Check Celery configuration in settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)

# Start with debug mode
celery -A config worker --loglevel=debug
```

### Issue 2: Emails Not Sending

**Symptoms**: Notifications created but `email_sent=False`

**Solution**:
```python
# Check notification preferences
from apps.notifications.models import NotificationPreference
from apps.accounts.models import User

user = User.objects.first()
prefs = NotificationPreference.objects.get(user=user)
print(f"Email enabled: {prefs.order_updates_email}")

# Check template exists
from apps.notifications.models import NotificationTemplate
template = NotificationTemplate.objects.get(type='order_created')
print(f"Template active: {template.is_active}")

# Manually trigger email
from apps.notifications.tasks import send_notification_email
from apps.notifications.models import Notification

notif = Notification.objects.filter(email_sent=False).first()
send_notification_email(str(notif.id))
```

### Issue 3: Template Rendering Errors

**Symptoms**: Email sent but looks broken

**Solution**:
```python
# Test template rendering
from django.template.loader import render_to_string

context = {
    'user': user,
    'order': order,
    'action_url': 'https://example.com'
}

try:
    html = render_to_string('emails/order/order_created.html', context)
    print("Template rendered successfully")
except Exception as e:
    print(f"Error: {e}")
```

### Issue 4: Signals Not Firing

**Symptoms**: Notifications not auto-created on order/payment changes

**Solution**:
```python
# Check signals are connected
from apps.notifications import signals
import inspect

# Check if signals module is imported in apps.py
from apps.notifications.apps import NotificationsConfig
print(inspect.getsource(NotificationsConfig.ready))

# Manually trigger signal
from django.db.models.signals import post_save
from apps.orders.models import Order

order = Order.objects.first()
post_save.send(sender=Order, instance=order, created=False)
```

### Issue 5: Migration Issues

**Symptoms**: `python manage.py migrate` fails

**Solution**:
```bash
# Show migrations
python manage.py showmigrations notifications

# If needed, fake migrations
python manage.py migrate notifications --fake

# Or start fresh (CAUTION: loses data)
python manage.py migrate notifications zero
python manage.py migrate notifications
```

---

## Performance Testing

### Load Testing with Multiple Notifications

```python
from apps.notifications.utils import create_notification
from apps.accounts.models import User
import time

user = User.objects.first()

# Create 100 notifications
start = time.time()
for i in range(100):
    create_notification(
        user=user,
        notification_type='general',
        context_data={'title': f'Test {i}', 'message': f'Message {i}'}
    )
end = time.time()

print(f"Created 100 notifications in {end - start:.2f} seconds")
print(f"Average: {(end - start) / 100 * 1000:.2f}ms per notification")
```

### Email Sending Performance

```python
from apps.notifications.tasks import send_notification_email
from apps.notifications.models import Notification
import time

# Get unsent notifications
notifications = Notification.objects.filter(email_sent=False)[:10]

start = time.time()
tasks = []
for notif in notifications:
    task = send_notification_email.delay(str(notif.id))
    tasks.append(task)

# Wait for all tasks
for task in tasks:
    task.get(timeout=30)

end = time.time()
print(f"Sent {len(tasks)} emails in {end - start:.2f} seconds")
```

---

## Cleanup After Testing

```python
# Delete test notifications
from apps.notifications.models import Notification

# Delete all test notifications
Notification.objects.filter(
    type='general',
    title__startswith='Test'
).delete()

# Or delete all notifications (CAUTION)
# Notification.objects.all().delete()
```

---

## Next Steps

After testing is complete:

1. ✅ Verify all 21 notification types work
2. ✅ Confirm emails are sent asynchronously
3. ✅ Test all API endpoints
4. ✅ Verify signal handlers work
5. ✅ Load test with 100+ notifications
6. 📝 Document any issues found
7. 🚀 Deploy to staging environment

---

**Testing Completed By**: [Your Name]
**Date**: [Date]
**Issues Found**: [List any issues]
**Status**: [Pass/Fail]

---

Generated with [Claude Code](https://claude.com/claude-code)
