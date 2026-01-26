# Phase 7: Enhanced Real-time Features - Implementation Plan

**Date**: 2026-01-02
**Phase**: 7 of 20-week implementation plan
**Status**: Planning → Implementation

---

## Overview

Extend the real-time capabilities with SMS notifications, browser push notifications, live chat, and advanced location tracking features.

---

## Current Infrastructure (Available)

### ✅ Already Implemented
- **WebSockets**: Django Channels with Redis
- **Email Notifications**: 21+ email templates
- **Real-time Updates**: Notifications and order tracking
- **JWT Authentication**: For WebSocket connections
- **Celery**: Async task processing
- **Redis**: Message broker and cache

### 🆕 To Be Added
- **SMS Gateway**: Twilio integration
- **Push Notifications**: Web Push API (PWA)
- **Live Chat**: Real-time messaging system
- **Location Tracking**: Real-time GPS updates
- **File Uploads**: Image/document sharing in chat

---

## Phase 7 Components

### 1. SMS Notifications (Priority: High)

**Goal**: Send SMS notifications for critical events

**Provider**: Twilio (recommended)
- Easy integration
- Reliable delivery
- Global coverage
- Affordable pricing
- Good Python SDK

**Implementation**:
```python
# apps/notifications/sms.py
from twilio.rest import Client

class SMSService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def send_sms(self, to_number, message):
        """Send SMS notification"""
        return self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_number
        )
```

**SMS Templates**:
- Order confirmed
- Order out for delivery
- Order delivered
- Payment confirmation
- Refund processed
- Partner order assignment (urgent)

**Features**:
- User preference for SMS (opt-in/opt-out)
- Phone number verification
- SMS delivery tracking
- Cost tracking per SMS
- Fallback to email if SMS fails

---

### 2. Browser Push Notifications (Priority: High)

**Goal**: Native browser notifications even when app is closed

**Technology**: Web Push API + Service Workers

**Implementation Strategy**:

#### Backend: Push Notification Service
```python
# apps/notifications/push.py
from pywebpush import webpush
import json

class PushNotificationService:
    def send_push_notification(self, subscription_info, notification_data):
        """Send push notification to browser"""
        return webpush(
            subscription_info=subscription_info,
            data=json.dumps(notification_data),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": "mailto:admin@laundryconnect.com"
            }
        )
```

#### Frontend: Service Worker
```javascript
// service-worker.js
self.addEventListener('push', function(event) {
    const data = event.data.json();

    const options = {
        body: data.message,
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png',
        data: {
            url: data.action_url
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});
```

**Models**:
```python
class PushSubscription(models.Model):
    user = ForeignKey(User)
    endpoint = URLField()
    p256dh_key = CharField(max_length=255)
    auth_key = CharField(max_length=255)
    device_name = CharField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)
```

**Features**:
- Multiple device support per user
- Subscribe/unsubscribe API
- Push notification preferences
- Rich notifications with images
- Action buttons in notifications
- Click tracking

---

### 3. Live Chat System (Priority: Medium)

**Goal**: Real-time messaging between customers and partners

**Architecture**:

#### Models
```python
class ChatRoom(models.Model):
    room_id = CharField(unique=True)  # Format: CHAT{YYYYMMDD}{8-char}
    order = ForeignKey(Order)
    customer = ForeignKey(User, related_name='customer_chats')
    partner = ForeignKey(Partner)
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)
    last_message_at = DateTimeField(null=True)

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('location', 'Location'),
        ('system', 'System Message'),
    ]

    id = UUIDField(primary_key=True)
    room = ForeignKey(ChatRoom)
    sender = ForeignKey(User)
    message_type = CharField(choices=MESSAGE_TYPES)
    content = TextField()  # Text or file URL
    metadata = JSONField(default=dict)  # Location coords, file info, etc.
    is_read = BooleanField(default=False)
    read_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### WebSocket Consumer
```python
class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive_json(self, content):
        message_type = content.get('type')

        if message_type == 'chat_message':
            await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': content['message'],
                    'sender': content['sender'],
                    'timestamp': timezone.now().isoformat()
                }
            )
```

**Features**:
- Real-time messaging
- Typing indicators
- Message delivery receipts
- Read receipts
- File sharing (images, PDFs)
- Location sharing
- Message history
- Unread count
- Push notifications for new messages
- System messages (order status updates)

---

### 4. Real-time Location Tracking (Priority: Medium)

**Goal**: Track delivery partner location in real-time on map

**Implementation**:

#### Model
```python
class LocationUpdate(models.Model):
    order = ForeignKey(Order)
    partner = ForeignKey(Partner)
    latitude = DecimalField(max_digits=9, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    accuracy = FloatField()  # meters
    speed = FloatField(null=True)  # km/h
    heading = FloatField(null=True)  # degrees
    timestamp = DateTimeField(auto_now_add=True)
```

#### API Endpoint
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_location(request, order_id):
    """Partner updates their location during delivery"""
    # Validate partner is assigned to order
    # Save location to database
    # Broadcast to WebSocket

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'order_{order_id}',
        {
            'type': 'location_update',
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp
        }
    )
```

#### Frontend (Google Maps/Mapbox)
```javascript
// Update marker position in real-time
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'location') {
        updateDeliveryMarker(data.latitude, data.longitude);
        calculateETA(data.latitude, data.longitude);
    }
};
```

**Features**:
- Live partner location on map
- Route display
- ETA calculation
- Geofencing alerts
- Location history/trail
- Privacy controls
- Battery optimization

---

## Implementation Timeline

### Week 1: SMS Notifications (Days 1-3)

**Day 1**:
- Install Twilio SDK
- Create SMS service module
- Add SMS templates
- Phone number verification

**Day 2**:
- Integrate with notification signals
- User SMS preferences
- Test SMS delivery
- Error handling

**Day 3**:
- SMS cost tracking
- Delivery reports
- Testing and documentation

### Week 2: Push Notifications (Days 4-6)

**Day 4**:
- Install pywebpush
- Create subscription model
- VAPID key generation
- Subscribe/unsubscribe API

**Day 5**:
- Service worker setup
- Push notification service
- Integration with signals
- Testing

**Day 6**:
- Rich notifications
- Action buttons
- Click tracking
- Documentation

### Week 3: Live Chat (Days 7-11)

**Day 7-8**:
- Create chat models
- Migrations
- Admin interface
- Basic CRUD APIs

**Day 9-10**:
- Chat WebSocket consumer
- Message broadcasting
- Typing indicators
- Read receipts

**Day 11**:
- File upload support
- Message history
- Testing
- Documentation

### Week 4: Location Tracking (Days 12-14)

**Day 12**:
- Location model
- Update location API
- WebSocket broadcasting

**Day 13**:
- Frontend map integration
- Real-time marker updates
- Route display
- ETA calculation

**Day 14**:
- Testing
- Privacy controls
- Documentation
- Final integration

---

## Files to Create

### SMS Notifications
1. `apps/notifications/sms.py` - SMS service
2. `apps/notifications/management/commands/test_sms.py` - Testing command

### Push Notifications
1. `apps/notifications/push.py` - Push notification service
2. `apps/notifications/models.py` - Add PushSubscription model
3. `apps/notifications/migrations/000X_push_subscription.py`
4. `apps/notifications/views.py` - Subscribe/unsubscribe endpoints
5. `static/js/service-worker.js` - Service worker
6. `static/js/push-notifications.js` - Push notification client

### Live Chat
1. `apps/chat/__init__.py` - New app
2. `apps/chat/models.py` - ChatRoom, ChatMessage
3. `apps/chat/consumers.py` - ChatConsumer
4. `apps/chat/serializers.py` - Chat serializers
5. `apps/chat/views.py` - Chat API
6. `apps/chat/routing.py` - WebSocket routing
7. `apps/chat/urls.py` - HTTP routing

### Location Tracking
1. `apps/tracking/__init__.py` - New app
2. `apps/tracking/models.py` - LocationUpdate
3. `apps/tracking/views.py` - Location API
4. `apps/tracking/serializers.py`
5. `apps/tracking/urls.py`

### Documentation
1. `PHASE_7_SUMMARY.md` - Implementation summary
2. `SMS_INTEGRATION_GUIDE.md` - SMS setup guide
3. `PUSH_NOTIFICATION_GUIDE.md` - Push notification guide
4. `LIVE_CHAT_GUIDE.md` - Chat integration guide

---

## Environment Variables

```bash
# Twilio SMS
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Web Push (VAPID)
VAPID_PUBLIC_KEY=your-public-key
VAPID_PRIVATE_KEY=your-private-key
VAPID_ADMIN_EMAIL=admin@laundryconnect.com

# Google Maps (for location tracking)
GOOGLE_MAPS_API_KEY=your-api-key
```

---

## Dependencies

```txt
# requirements/base.txt additions
twilio==8.10.0                  # SMS notifications
pywebpush==1.14.0               # Web push notifications
py-vapid==1.9.0                 # VAPID for push
```

---

## Success Criteria

- [ ] SMS notifications sent for critical events
- [ ] Users can opt-in/out of SMS
- [ ] Browser push notifications working
- [ ] Service worker installed and active
- [ ] Live chat between customer and partner
- [ ] Real-time location tracking on map
- [ ] File sharing in chat
- [ ] All features documented
- [ ] Tests passing

---

## Future Enhancements (Phase 8+)

1. **Voice Calls**: Twilio Voice integration
2. **Video Chat**: WebRTC video calls
3. **AI Chatbot**: Automated customer support
4. **Multi-language**: SMS and chat in local languages
5. **Rich Media**: GIFs, stickers in chat
6. **Group Chat**: Support team chat
7. **Analytics**: Chat analytics, response times

---

**Next Step**: Start with SMS notifications (highest priority, easiest to implement)

---

Generated with [Claude Code](https://claude.com/claude-code)
