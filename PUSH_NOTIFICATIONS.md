# Push Notifications - LaundryConnect

This document describes the Web Push Notification system implementation for LaundryConnect.

## Overview

LaundryConnect implements Web Push Notifications using the Push API and VAPID (Voluntary Application Server Identification) protocol. This allows the platform to send real-time notifications to users' browsers even when they're not actively viewing the site.

## Features

- **Browser Push Notifications**: Send notifications to users' browsers using the Web Push API
- **VAPID Authentication**: Secure push notifications using VAPID keys
- **Multi-Device Support**: Users can subscribe from multiple devices/browsers
- **Subscription Management**: Users can manage their push subscriptions
- **Offline Support**: Service worker provides offline functionality
- **User Preferences**: Granular control over notification types
- **Auto-cleanup**: Expired subscriptions are automatically deactivated

## Architecture

### Components

1. **Backend Components**:
   - `PushSubscription` model: Stores push subscription data
   - `PushNotificationService`: Handles sending push notifications
   - `send_push_notification` task: Async task for sending push
   - Signal handlers: Trigger push notifications on events

2. **Frontend Components**:
   - `service-worker.js`: Handles push events and notifications
   - `push-notifications.js`: Client-side push subscription management
   - UI for subscription management

3. **Dependencies**:
   - `py-vapid`: VAPID key generation and management
   - `pywebpush`: Sending web push notifications
   - Browser Push API support

## Setup

### 1. Install Dependencies

Push notification dependencies are already in `requirements/base.txt`:

```txt
py-vapid==1.9.1
pywebpush==1.14.1
```

Install them:

```bash
pip install -r requirements/base.txt
```

### 2. Generate VAPID Keys

Generate VAPID keys for your application:

```bash
python manage.py generate_vapid_keys
```

This will output:
- `VAPID_PRIVATE_KEY`: Private key (keep secret!)
- `VAPID_PUBLIC_KEY`: Public key (share with browsers)
- `VAPID_ADMIN_EMAIL`: Contact email (mailto:your@email.com)

### 3. Configure Environment Variables

Add the generated keys to your `.env` file:

```env
# Web Push Notifications (VAPID)
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----"
VAPID_PUBLIC_KEY="BGz8P1k..."
VAPID_ADMIN_EMAIL="mailto:admin@laundryconnect.com"
```

**Important**: Never commit your private key to version control!

### 4. Run Migrations

The migrations for push notifications are already included:

```bash
python manage.py migrate notifications
```

### 5. Configure Static Files

Ensure static files are collected for production:

```bash
python manage.py collectstatic
```

The service worker and push client files are in:
- `/static/js/service-worker.js`
- `/static/js/push-notifications.js`

## Usage

### Backend Usage

#### Sending Push Notifications

Push notifications are sent automatically when notifications are created through signals:

```python
from apps.notifications.utils import create_notification

# Create a notification (push is sent automatically)
notification = create_notification(
    user=user,
    notification_type='order_created',
    order=order
)
```

#### Manual Push Sending

To send a push notification manually:

```python
from apps.notifications.tasks import send_push_notification

# Send push for existing notification
send_push_notification.delay(str(notification.id))
```

#### Direct Push API Usage

For more control, use the push service directly:

```python
from apps.notifications.push import push_service
from apps.notifications.models import PushSubscription

# Get user's subscriptions
subscriptions = PushSubscription.objects.filter(
    user=user,
    is_active=True
)

# Send to each subscription
for subscription in subscriptions:
    push_data = {
        'title': 'Hello!',
        'body': 'This is a test notification',
        'icon': '/static/images/logo-192x192.png',
        'data': {'url': '/orders/123'}
    }

    result = push_service.send_push_notification(
        subscription.get_subscription_info(),
        push_data
    )

    if result['success']:
        print('Push sent successfully!')
    else:
        print(f'Error: {result["error"]}')
```

### Frontend Usage

#### 1. Include Scripts in Your HTML

```html
<!-- In your base template -->
<script src="{% static 'js/push-notifications.js' %}"></script>
```

#### 2. Initialize Push Client

```javascript
// Get VAPID public key from Django template context
const vapidPublicKey = '{{ VAPID_PUBLIC_KEY }}';

// Initialize push notifications
initPushNotifications(vapidPublicKey)
    .then(client => {
        console.log('Push client initialized');
    });
```

#### 3. Subscribe User to Push

```javascript
// Request permission and subscribe
subscribeToPush('My Device Name')
    .then(subscription => {
        console.log('Subscribed successfully!', subscription);
        // Update UI to show subscription status
    })
    .catch(error => {
        console.error('Failed to subscribe:', error);
    });
```

#### 4. Unsubscribe User

```javascript
// Unsubscribe from push
unsubscribeFromPush()
    .then(success => {
        if (success) {
            console.log('Unsubscribed successfully!');
        }
    });
```

#### 5. Check Subscription Status

```javascript
// Check if user is subscribed
const permission = getNotificationPermission();
console.log('Permission status:', permission); // 'granted', 'denied', or 'default'

// Check browser support
if (isPushSupported()) {
    console.log('Push notifications are supported!');
} else {
    console.log('Push notifications are not supported in this browser');
}
```

### API Endpoints

#### Subscribe to Push Notifications

```http
POST /api/v1/notifications/push-subscriptions/
Content-Type: application/json

{
    "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    "keys": {
        "p256dh": "BMz8P1...",
        "auth": "8xP..."
    },
    "device_name": "Chrome on MacBook"
}
```

**Response:**

```json
{
    "id": "uuid",
    "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    "device_name": "Chrome on MacBook",
    "is_active": true,
    "created_at": "2025-01-03T10:30:00Z"
}
```

#### List User's Subscriptions

```http
GET /api/v1/notifications/push-subscriptions/
```

**Response:**

```json
[
    {
        "id": "uuid",
        "endpoint": "https://fcm.googleapis.com/fcm/send/...",
        "device_name": "Chrome on MacBook",
        "is_active": true,
        "created_at": "2025-01-03T10:30:00Z"
    }
]
```

#### Unsubscribe from Push

```http
POST /api/v1/notifications/push-subscriptions/unsubscribe/
Content-Type: application/json

{
    "endpoint": "https://fcm.googleapis.com/fcm/send/..."
}
```

#### Test Push Notification (Admin Only)

In Django Admin, you can send test push notifications:
1. Go to Notifications → Push Subscriptions
2. Select subscriptions
3. Choose "Send test push notification" action

## Service Worker

### Registration

The service worker is automatically registered when you initialize push notifications:

```javascript
// Service worker is registered at /static/js/service-worker.js
await navigator.serviceWorker.register('/static/js/service-worker.js');
```

### Features

The service worker provides:

1. **Push Event Handling**: Displays notifications when push is received
2. **Notification Clicks**: Opens relevant page when notification is clicked
3. **Offline Support**: Caches static assets for offline access
4. **Background Sync**: Syncs notification status (future enhancement)

### Customization

You can customize the service worker behavior by editing:
- `/static/js/service-worker.js`

Key areas to customize:
- Notification display options
- Click behavior
- Cache strategy
- Background sync logic

## User Preferences

Users can control push notifications through their notification preferences:

```python
from apps.notifications.models import NotificationPreference

# Get user preferences
prefs = NotificationPreference.objects.get(user=user)

# Enable/disable push for order updates
prefs.order_updates_push = True
prefs.save()

# Enable/disable push for payment updates
prefs.payment_updates_push = False
prefs.save()
```

Available push preference fields:
- `order_updates_push`
- `payment_updates_push`
- `refund_updates_push`
- `partner_updates_push`
- `promotional_push`

## Notification Types

Push notifications are sent for these event types:

### Order Notifications
- `order_created`: New order created
- `order_confirmed`: Order confirmed
- `order_processing`: Order being processed
- `order_ready`: Order ready for pickup
- `order_completed`: Order completed
- `order_cancelled`: Order cancelled

### Payment Notifications
- `payment_initiated`: Payment started
- `payment_completed`: Payment successful
- `payment_failed`: Payment failed
- `payment_refunded`: Payment refunded

### Refund Notifications
- `refund_requested`: Refund requested
- `refund_processing`: Refund being processed
- `refund_completed`: Refund completed
- `refund_failed`: Refund failed

### Partner Notifications
- `partner_approved`: Partner account approved

## Browser Support

Web Push Notifications are supported in:

- ✅ Chrome 42+
- ✅ Firefox 44+
- ✅ Edge 17+
- ✅ Opera 37+
- ✅ Safari 16+ (macOS 13+, iOS 16.4+)
- ❌ Internet Explorer (not supported)

**Note**: Safari requires macOS 13+ or iOS 16.4+ for push notification support.

## Security

### VAPID Keys

- **Private Key**: Keep secret! Never commit to version control
- **Public Key**: Safe to share with browsers
- Store private key in environment variables

### Subscription Data

- Endpoints are browser-specific and can't be used by others
- Keys (`p256dh`, `auth`) are encrypted
- Subscriptions are tied to authenticated users

### Best Practices

1. Never log or display private keys
2. Use HTTPS (required for service workers)
3. Validate subscription data on backend
4. Regularly clean up expired subscriptions
5. Respect user preferences

## Testing

### Test in Browser

1. Open browser DevTools → Application → Service Workers
2. Check if service worker is registered
3. Test push using "Push" button in DevTools

### Test from Admin

1. Login to Django Admin
2. Go to Notifications → Push Subscriptions
3. Select a subscription
4. Run "Send test push notification" action

### Test from Code

```python
from apps.notifications.push import push_service

# Check if push is enabled
if push_service.is_enabled():
    print('Push service is configured')
else:
    print('Push service is not configured')

# Send test notification
from apps.notifications.models import PushSubscription

subscription = PushSubscription.objects.filter(is_active=True).first()
if subscription:
    result = push_service.send_push_notification(
        subscription.get_subscription_info(),
        {
            'title': 'Test',
            'body': 'This is a test',
            'icon': '/static/images/logo.png'
        }
    )
    print(f'Result: {result}')
```

## Troubleshooting

### Push not working

1. **Check VAPID configuration**:
   ```python
   from django.conf import settings
   print(settings.VAPID_PUBLIC_KEY)  # Should not be empty
   print(settings.VAPID_PRIVATE_KEY)  # Should not be empty
   ```

2. **Check service worker registration**:
   - Open DevTools → Application → Service Workers
   - Verify service worker is "Activated and running"

3. **Check notification permission**:
   ```javascript
   console.log(Notification.permission); // Should be "granted"
   ```

4. **Check subscription**:
   ```javascript
   navigator.serviceWorker.ready.then(registration => {
       registration.pushManager.getSubscription().then(sub => {
           console.log('Subscription:', sub);
       });
   });
   ```

### Notifications not displaying

1. Check browser notification settings
2. Verify notification permission is granted
3. Check service worker console for errors
4. Verify payload format is correct

### Subscriptions expiring

- This is normal - browsers can expire subscriptions
- Expired subscriptions are automatically deactivated
- Users should re-subscribe if needed

## Performance

### Optimization Tips

1. **Batch notifications**: Don't send too many at once
2. **Use TTL**: Set appropriate time-to-live for messages
3. **Clean old subscriptions**: Run cleanup task regularly
4. **Use Celery**: All push sending is async via Celery
5. **Monitor failures**: Check logs for delivery issues

### Celery Configuration

Push notifications use Celery for async processing:

```python
# Task configuration
@shared_task(bind=True, max_retries=3)
def send_push_notification(self, notification_id):
    # Retries 3 times with 5-minute delays
    pass
```

## Monitoring

### Check Push Statistics

```python
from apps.notifications.models import Notification, PushSubscription

# Total active subscriptions
active_subs = PushSubscription.objects.filter(is_active=True).count()
print(f'Active subscriptions: {active_subs}')

# Notifications with push metadata
push_sent = Notification.objects.filter(
    metadata__push__sent=True
).count()
print(f'Notifications with push sent: {push_sent}')
```

### Logs

Check logs for push-related messages:

```bash
# Check for push errors
grep "push" logs/celery.log

# Check for expired subscriptions
grep "expired" logs/celery.log
```

## Future Enhancements

Potential improvements:

1. **Rich Notifications**: Images, action buttons, custom sounds
2. **Notification Channels**: Group notifications by category
3. **Priority Levels**: Urgent vs normal notifications
4. **Delivery Reports**: Track notification open rates
5. **A/B Testing**: Test notification content
6. **Scheduled Push**: Send at optimal times
7. **Geolocation**: Location-based notifications

## Resources

- [Web Push Protocol](https://datatracker.ietf.org/doc/html/rfc8030)
- [VAPID Specification](https://datatracker.ietf.org/doc/html/rfc8292)
- [Push API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Notification API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)

## Support

For issues or questions:
1. Check this documentation
2. Review browser console for errors
3. Check Django logs
4. Verify VAPID configuration
5. Test with different browsers
