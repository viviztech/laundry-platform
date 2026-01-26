# Phase 6: Real-time Features & WebSockets - Implementation Plan

**Date**: 2026-01-02
**Phase**: 6 of 20-week implementation plan
**Status**: Planning → Implementation

---

## Overview

Implement real-time features using Django Channels and WebSockets to enable live order tracking, instant notifications, and real-time updates without page refreshes.

---

## Current Infrastructure

### ✅ Already Available
- **Redis**: Running on localhost:6379 (also used by Celery)
- **Notification System**: Complete with 21+ notification types
- **Order Management**: Full order lifecycle tracking
- **User Authentication**: JWT-based auth system
- **Django REST Framework**: API foundation

### 🆕 To Be Added
- **Django Channels**: WebSocket support
- **Channel Layers**: Redis-based message passing
- **ASGI Server**: Daphne or Uvicorn
- **WebSocket Consumers**: Real-time message handlers
- **Frontend Integration**: WebSocket client connections

---

## Phase 6 Objectives

### 1. WebSocket Infrastructure
- Install and configure Django Channels
- Set up ASGI application
- Configure channel layers with Redis
- Create WebSocket routing

### 2. Real-time Notifications
- Live notification delivery to connected clients
- Unread count updates in real-time
- Notification bell with live updates
- Browser push notifications

### 3. Order Tracking
- Live order status updates
- Real-time location tracking (partner)
- ETA updates
- Live chat with partner (optional)

### 4. Partner Features
- Real-time order assignments
- Live order queue updates
- Instant customer communication
- Real-time earnings updates

### 5. Admin Features
- Live dashboard updates
- Real-time order monitoring
- System health monitoring
- Live user activity tracking

---

## Architecture Design

### WebSocket Connection Flow

```
Client (Browser/Mobile)
    ↓ WebSocket Connection
ASGI Server (Daphne)
    ↓ Routing
WebSocket Consumer
    ↓ Channel Layer (Redis)
Message Broadcasting
    ↓ All Connected Clients
Live Updates
```

### Channel Groups

1. **User Personal Channel**: `user_{user_id}`
   - Personal notifications
   - Order updates for user's orders
   - Wallet updates

2. **Partner Channel**: `partner_{partner_id}`
   - New order assignments
   - Customer messages
   - Earnings updates

3. **Order Channel**: `order_{order_id}`
   - Order status updates
   - All parties involved in the order
   - Real-time tracking

4. **Admin Channel**: `admin_dashboard`
   - System-wide updates
   - New orders
   - Payment events

---

## Implementation Strategy

### Phase 6.1: Django Channels Setup (Day 1)

#### Install Dependencies
```bash
pip install channels[daphne]==4.0.0
pip install channels-redis==4.1.0
```

#### Update Settings
```python
# config/settings/base.py
INSTALLED_APPS = [
    'daphne',  # Must be first
    'django.contrib.admin',
    # ... other apps
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

#### Create ASGI Configuration
```python
# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

from apps.realtime import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
```

---

### Phase 6.2: Create Realtime App (Day 1)

#### App Structure
```
apps/realtime/
├── __init__.py
├── apps.py
├── consumers.py          # WebSocket consumers
├── routing.py            # WebSocket URL routing
├── middleware.py         # JWT authentication for WS
├── utils.py              # Helper functions
├── serializers.py        # Message serializers
└── tests.py
```

#### WebSocket Consumers

**NotificationConsumer**
```python
# apps/realtime/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Get user from scope (JWT auth)
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Join user's personal channel
        self.group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial unread count
        unread_count = await self.get_unread_count()
        await self.send_json({
            'type': 'unread_count',
            'count': unread_count
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        # Handle incoming messages
        message_type = content.get('type')

        if message_type == 'mark_read':
            await self.mark_notification_read(content['id'])
        elif message_type == 'mark_all_read':
            await self.mark_all_notifications_read()

    # Message handlers
    async def notification_message(self, event):
        await self.send_json({
            'type': 'notification',
            'notification': event['notification']
        })

    async def unread_count_update(self, event):
        await self.send_json({
            'type': 'unread_count',
            'count': event['count']
        })

    @database_sync_to_async
    def get_unread_count(self):
        from apps.notifications.utils import get_unread_count
        return get_unread_count(self.user)
```

**OrderTrackingConsumer**
```python
class OrderTrackingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.order_id = self.scope['url_route']['kwargs']['order_id']

        if not await self.can_access_order():
            await self.close()
            return

        self.group_name = f'order_{self.order_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send current order status
        order_data = await self.get_order_data()
        await self.send_json({
            'type': 'order_status',
            'order': order_data
        })

    async def order_update(self, event):
        await self.send_json({
            'type': 'order_update',
            'update': event['data']
        })

    async def location_update(self, event):
        await self.send_json({
            'type': 'location',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp']
        })
```

---

### Phase 6.3: JWT WebSocket Authentication (Day 2)

#### Custom Middleware
```python
# apps/realtime/middleware.py
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import User

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token.payload.get('user_id')
        return User.objects.get(id=user_id)
    except:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(qp.split('=') for qp in query_string.split('&') if '=' in qp)
        token = query_params.get('token')

        # Or from headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
```

---

### Phase 6.4: Signal Integration (Day 2)

#### Update Notification Signals
```python
# apps/notifications/signals.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_notification(user_id, notification_data):
    """Broadcast notification to user's WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        # Send email (existing)
        send_notification_email.delay(str(instance.id))

        # Broadcast via WebSocket (new)
        notification_data = {
            'id': str(instance.id),
            'type': instance.type,
            'title': instance.title,
            'message': instance.message,
            'created_at': instance.created_at.isoformat()
        }
        broadcast_notification(str(instance.user.id), notification_data)
```

#### Update Order Signals
```python
# apps/orders/signals.py (to be created)
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created:
        # Broadcast to order channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'order_{instance.id}',
            {
                'type': 'order_update',
                'data': {
                    'status': instance.status,
                    'updated_at': instance.updated_at.isoformat()
                }
            }
        )
```

---

### Phase 6.5: REST API Extensions (Day 3)

#### WebSocket Token Endpoint
```python
# apps/realtime/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_websocket_token(request):
    """Get a token for WebSocket authentication"""
    token = AccessToken.for_user(request.user)
    return Response({
        'token': str(token),
        'ws_url': f'ws://localhost:8000/ws/notifications/?token={str(token)}'
    })
```

---

### Phase 6.6: Frontend Integration Guide (Day 3)

#### JavaScript WebSocket Client
```javascript
// Example WebSocket connection
class NotificationWebSocket {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.reconnectInterval = 3000;
    }

    connect() {
        this.ws = new WebSocket(
            `ws://localhost:8000/ws/notifications/?token=${this.token}`
        );

        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(() => this.connect(), this.reconnectInterval);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(data) {
        switch(data.type) {
            case 'notification':
                this.showNotification(data.notification);
                this.updateUnreadCount();
                break;
            case 'unread_count':
                this.updateBadge(data.count);
                break;
        }
    }

    markAsRead(notificationId) {
        this.ws.send(JSON.stringify({
            type: 'mark_read',
            id: notificationId
        }));
    }
}

// Usage
const token = await getWebSocketToken();
const notificationWS = new NotificationWebSocket(token);
notificationWS.connect();
```

---

## Files to Create

### New App: `apps/realtime/`
1. `__init__.py`
2. `apps.py`
3. `consumers.py` - WebSocket consumers
4. `routing.py` - WebSocket URL patterns
5. `middleware.py` - JWT authentication
6. `utils.py` - Helper functions
7. `serializers.py` - Message serializers
8. `views.py` - WebSocket token API
9. `urls.py` - HTTP endpoints
10. `tests.py`

### Updates to Existing Files
1. `config/settings/base.py` - Add channels configuration
2. `config/asgi.py` - Configure ASGI application
3. `config/urls.py` - Add realtime URLs
4. `apps/notifications/signals.py` - Add WebSocket broadcasting
5. `apps/orders/signals.py` - Add order update broadcasting
6. `requirements/base.txt` - Add channels dependencies

### Documentation
1. `PHASE_6_PLAN.md` - This file
2. `PHASE_6_WEBSOCKET_GUIDE.md` - WebSocket usage guide
3. `REALTIME_API_DOCS.md` - Real-time API documentation

---

## Testing Strategy

### Unit Tests
- Consumer connection/disconnection
- Message routing
- JWT authentication
- Channel layer messaging

### Integration Tests
- End-to-end notification delivery
- Order update broadcasting
- Multi-client scenarios
- Reconnection handling

### Load Tests
- 100+ concurrent connections
- Message broadcast performance
- Channel layer throughput

---

## Dependencies

```txt
# requirements/base.txt additions
channels[daphne]==4.0.0
channels-redis==4.1.0
```

---

## Running the Application

### Development
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A config worker -l info

# Terminal 3: Django + WebSocket
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Or use runserver (auto-detects channels)
python manage.py runserver
```

### Production
```bash
# Use supervisor or systemd
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

---

## Success Criteria

- [ ] Django Channels installed and configured
- [ ] WebSocket consumers implemented
- [ ] JWT authentication working for WebSockets
- [ ] Real-time notifications delivered
- [ ] Order updates broadcast in real-time
- [ ] Frontend integration guide created
- [ ] Tests passing
- [ ] Documentation complete

---

## Timeline

**Estimated Time**: 3-4 days

- **Day 1**: Setup Channels, create consumers
- **Day 2**: JWT auth, signal integration
- **Day 3**: API endpoints, testing
- **Day 4**: Documentation, polish

---

## Future Enhancements (Phase 7+)

1. **Live Chat**: Customer-Partner messaging
2. **Location Tracking**: Real-time GPS tracking
3. **Video Calls**: Partner video support
4. **Screen Sharing**: Support sessions
5. **Collaborative Features**: Multi-admin dashboards

---

**Next Step**: Start implementation with Django Channels setup

---

Generated with [Claude Code](https://claude.com/claude-code)
