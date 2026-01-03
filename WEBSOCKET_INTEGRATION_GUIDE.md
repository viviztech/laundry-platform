# WebSocket Integration Guide - LaundryConnect

**Last Updated**: 2026-01-02
**Phase**: 6 - Real-time Features

---

## Overview

This guide provides complete instructions for integrating real-time WebSocket features into your frontend application. LaundryConnect supports real-time notifications, order tracking, and partner updates via WebSockets.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting a WebSocket Token](#getting-a-websocket-token)
3. [Connecting to WebSockets](#connecting-to-websockets)
4. [Notification WebSocket](#notification-websocket)
5. [Order Tracking WebSocket](#order-tracking-websocket)
6. [Partner WebSocket](#partner-websocket)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Code Examples](#code-examples)

---

## Prerequisites

### Backend Requirements
- Django server running with Channels
- Redis server running (for channel layer)
- Celery worker running (for async tasks)

### Frontend Requirements
- Modern browser with WebSocket support
- Valid JWT authentication token
- Axios or Fetch API for HTTP requests

---

## Getting a WebSocket Token

Before connecting to WebSockets, you need to get a WebSocket token from the API.

### Endpoint
```
GET /api/realtime/token/
```

### Request Example

**Using Axios**:
```javascript
const getWebSocketToken = async () => {
    try {
        const response = await axios.get('/api/realtime/token/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        return response.data;
        // Returns:
        // {
        //     token: "eyJ0eXAi...",
        //     ws_base_url: "ws://localhost:8000/ws",
        //     endpoints: {
        //         notifications: "ws://localhost:8000/ws/notifications/?token=...",
        //         order_tracking: "ws://localhost:8000/ws/orders/{order_id}/?token=...",
        //         partner: "ws://localhost:8000/ws/partner/?token=..." (if partner)
        //     },
        //     expires_in: 3600,
        //     user_id: "uuid",
        //     is_partner: false
        // }
    } catch (error) {
        console.error('Failed to get WebSocket token:', error);
        throw error;
    }
};
```

**Using Fetch**:
```javascript
const getWebSocketToken = async () => {
    const response = await fetch('/api/realtime/token/', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });

    if (!response.ok) {
        throw new Error('Failed to get WebSocket token');
    }

    return await response.json();
};
```

---

## Connecting to WebSockets

### WebSocket URL Format

All WebSocket connections require a token parameter:

```
ws://localhost:8000/ws/<endpoint>/?token=YOUR_TOKEN
```

### Connection Process

1. Get WebSocket token from API
2. Open WebSocket connection with token
3. Wait for `connection_established` message
4. Start sending/receiving messages
5. Handle disconnections and reconnect

---

## Notification WebSocket

### Connection

**Endpoint**: `/ws/notifications/`

**Features**:
- Receive real-time notifications
- Get unread notification count
- Mark notifications as read
- Automatic reconnection

### JavaScript Client

```javascript
class NotificationWebSocket {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.reconnectInterval = 3000; // 3 seconds
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.isIntentionallyClosed = false;
        this.listeners = {};
    }

    connect() {
        const wsUrl = `ws://localhost:8000/ws/notifications/?token=${this.token}`;

        this.ws = new WebSocket(wsUrl);
        this.isIntentionallyClosed = false;

        this.ws.onopen = () => {
            console.log('✅ Notification WebSocket connected');
            this.reconnectAttempts = 0;
            this.emit('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('🔌 Notification WebSocket closed:', event.code);
            this.emit('disconnected', event.code);

            // Attempt to reconnect if not intentionally closed
            if (!this.isIntentionallyClosed) {
                this.attemptReconnect();
            }
        };

        this.ws.onerror = (error) => {
            console.error('❌ Notification WebSocket error:', error);
            this.emit('error', error);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('Connection established:', data.message);
                this.emit('connection_established', {
                    message: data.message,
                    unread_count: data.unread_count
                });
                break;

            case 'notification':
                console.log('New notification:', data.notification);
                this.emit('notification', data.notification);
                this.showNotification(data.notification);
                break;

            case 'unread_count':
                console.log('Unread count update:', data.count);
                this.emit('unread_count', data.count);
                this.updateBadge(data.count);
                break;

            case 'mark_read_response':
                console.log('Mark read response:', data);
                this.emit('mark_read_response', data);
                break;

            case 'pong':
                console.log('Received pong');
                break;

            case 'error':
                console.error('Server error:', data.message);
                this.emit('server_error', data.message);
                break;

            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    markAsRead(notificationId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.send({
                type: 'mark_read',
                notification_id: notificationId
            });
        }
    }

    markAllAsRead() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.send({
                type: 'mark_all_read'
            });
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }

    ping() {
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.emit('reconnect_failed');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }

    disconnect() {
        this.isIntentionallyClosed = true;
        if (this.ws) {
            this.ws.close();
        }
    }

    // Event listener system
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    // UI Update methods
    showNotification(notification) {
        // Show browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo.png',
                tag: notification.id
            });
        }

        // Update UI notification list
        this.emit('ui_notification', notification);
    }

    updateBadge(count) {
        // Update notification badge
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'block' : 'none';
        }
    }
}
```

### Usage Example

```javascript
// Initialize and connect
const initNotifications = async () => {
    // Get token
    const tokenData = await getWebSocketToken();

    // Create WebSocket instance
    const notificationWS = new NotificationWebSocket(tokenData.token);

    // Set up event listeners
    notificationWS.on('connected', () => {
        console.log('Successfully connected to notifications');
    });

    notificationWS.on('notification', (notification) => {
        console.log('New notification received:', notification);
        // Add to notification list in UI
        addNotificationToUI(notification);
    });

    notificationWS.on('unread_count', (count) => {
        console.log('Unread count:', count);
        updateNotificationBadge(count);
    });

    notificationWS.on('disconnected', (code) => {
        console.log('Disconnected with code:', code);
        showConnectionStatus('Reconnecting...');
    });

    notificationWS.on('reconnect_failed', () => {
        console.error('Failed to reconnect');
        showConnectionStatus('Connection lost');
    });

    // Connect
    notificationWS.connect();

    // Set up periodic ping (keep-alive)
    setInterval(() => {
        notificationWS.ping();
    }, 30000); // Every 30 seconds

    return notificationWS;
};

// Usage
let notificationWS;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        notificationWS = await initNotifications();

        // Mark notification as read when clicked
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('notification-item')) {
                const notificationId = e.target.dataset.notificationId;
                notificationWS.markAsRead(notificationId);
            }
        });

        // Mark all as read button
        document.querySelector('#mark-all-read')?.addEventListener('click', () => {
            notificationWS.markAllAsRead();
        });

    } catch (error) {
        console.error('Failed to initialize notifications:', error);
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (notificationWS) {
        notificationWS.disconnect();
    }
});
```

---

## Order Tracking WebSocket

### Connection

**Endpoint**: `/ws/orders/<order_id>/`

**Features**:
- Real-time order status updates
- Location tracking (for delivery)
- ETA updates

### JavaScript Client

```javascript
class OrderTrackingWebSocket {
    constructor(orderId, token) {
        this.orderId = orderId;
        this.token = token;
        this.ws = null;
        this.reconnectInterval = 3000;
        this.listeners = {};
    }

    connect() {
        const wsUrl = `ws://localhost:8000/ws/orders/${this.orderId}/?token=${this.token}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log(`✅ Order tracking connected for order ${this.orderId}`);
            this.emit('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('Order tracking WebSocket closed:', event.code);
            this.emit('disconnected', event.code);

            // Reconnect after delay
            setTimeout(() => this.connect(), this.reconnectInterval);
        };

        this.ws.onerror = (error) => {
            console.error('Order tracking WebSocket error:', error);
            this.emit('error', error);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('Order tracking established:', data.order);
                this.emit('order_data', data.order);
                this.updateOrderUI(data.order);
                break;

            case 'order_update':
                console.log('Order update:', data.update);
                this.emit('order_update', data.update);
                this.updateOrderStatus(data.update);
                break;

            case 'location':
                console.log('Location update:', data);
                this.emit('location_update', {
                    latitude: data.latitude,
                    longitude: data.longitude,
                    timestamp: data.timestamp
                });
                this.updateMapLocation(data);
                break;

            case 'pong':
                break;

            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    ping() {
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    // UI Update Methods
    updateOrderUI(order) {
        document.querySelector('#order-status').textContent = order.status_display;
        document.querySelector('#order-number').textContent = order.order_number;
        if (order.partner) {
            document.querySelector('#partner-name').textContent = order.partner.name;
        }
    }

    updateOrderStatus(update) {
        document.querySelector('#order-status').textContent = update.status_display;
        const statusTimeline = document.querySelector('#status-timeline');
        const statusItem = document.createElement('div');
        statusItem.className = 'timeline-item';
        statusItem.innerHTML = `
            <span class="status">${update.status_display}</span>
            <span class="time">${new Date(update.updated_at).toLocaleString()}</span>
        `;
        statusTimeline.appendChild(statusItem);
    }

    updateMapLocation(location) {
        if (typeof updateMap === 'function') {
            updateMap(location.latitude, location.longitude);
        }
    }
}
```

### Usage Example

```javascript
// Track a specific order
const trackOrder = async (orderId) => {
    // Get token
    const tokenData = await getWebSocketToken();

    // Create tracking instance
    const orderTracking = new OrderTrackingWebSocket(orderId, tokenData.token);

    // Set up event listeners
    orderTracking.on('order_data', (order) => {
        console.log('Order data:', order);
        displayOrderInfo(order);
    });

    orderTracking.on('order_update', (update) => {
        console.log('Order updated:', update);
        showToast(`Order status changed to ${update.status_display}`);
        updateOrderStatusUI(update);
    });

    orderTracking.on('location_update', (location) => {
        console.log('Location update:', location);
        updateDeliveryMap(location);
    });

    // Connect
    orderTracking.connect();

    return orderTracking;
};

// Usage on order tracking page
let orderTracking;

if (window.location.pathname.includes('/orders/')) {
    const orderId = getOrderIdFromURL();
    orderTracking = await trackOrder(orderId);
}
```

---

## Partner WebSocket

### Connection

**Endpoint**: `/ws/partner/`

**Features**:
- New order assignment notifications
- Earnings updates
- Customer messages

### JavaScript Client

```javascript
class PartnerWebSocket {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.listeners = {};
    }

    connect() {
        const wsUrl = `ws://localhost:8000/ws/partner/?token=${this.token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('✅ Partner WebSocket connected');
            this.emit('connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = (event) => {
            console.log('Partner WebSocket closed');
            this.emit('disconnected');
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                this.emit('established');
                break;

            case 'new_order':
                console.log('New order assignment:', data.order);
                this.emit('new_order', data.order);
                this.showOrderNotification(data.order);
                break;

            case 'earnings_update':
                console.log('Earnings updated:', data);
                this.emit('earnings_update', {
                    amount: data.amount,
                    total: data.total
                });
                this.updateEarnings(data);
                break;
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }

    showOrderNotification(order) {
        // Show new order alert
        alert(`New order assigned: ${order.order_number}`);
    }

    updateEarnings(data) {
        document.querySelector('#total-earnings').textContent = `₹${data.total}`;
    }
}
```

---

## Error Handling

### Connection Errors

```javascript
class WebSocketManager {
    handleConnectionError(error) {
        console.error('WebSocket connection error:', error);

        // Check if token expired
        if (error.code === 4001) {
            // Token expired or invalid
            this.refreshToken().then(newToken => {
                this.token = newToken;
                this.connect();
            });
        }

        // Check if forbidden
        else if (error.code === 4003) {
            // User doesn't have permission
            showError('You don\'t have permission to access this resource');
        }

        // Other errors
        else {
            showError('Connection failed. Please try again later.');
        }
    }

    async refreshToken() {
        const response = await axios.post('/api/accounts/token/refresh/', {
            refresh: localStorage.getItem('refresh_token')
        });
        return response.data.access;
    }
}
```

### Message Validation

```javascript
function validateMessage(data) {
    if (!data || typeof data !== 'object') {
        throw new Error('Invalid message format');
    }

    if (!data.type) {
        throw new Error('Message type missing');
    }

    return true;
}
```

---

## Best Practices

### 1. Token Management

```javascript
// Refresh token before it expires
class TokenManager {
    constructor(tokenData) {
        this.tokenData = tokenData;
        this.setupRefreshTimer();
    }

    setupRefreshTimer() {
        // Refresh 5 minutes before expiry
        const refreshTime = (this.tokenData.expires_in - 300) * 1000;

        setTimeout(async () => {
            const newData = await getWebSocketToken();
            this.tokenData = newData;
            this.onTokenRefreshed(newData);
            this.setupRefreshTimer();
        }, refreshTime);
    }

    onTokenRefreshed(newData) {
        // Notify all WebSocket connections to reconnect with new token
        console.log('Token refreshed');
    }
}
```

### 2. Reconnection Strategy

```javascript
class ReconnectionManager {
    constructor() {
        this.attempts = 0;
        this.maxAttempts = 10;
        this.baseDelay = 1000; // 1 second
    }

    getDelay() {
        // Exponential backoff: 1s, 2s, 4s, 8s, etc.
        return Math.min(this.baseDelay * Math.pow(2, this.attempts), 30000);
    }

    async reconnect(connectFunction) {
        if (this.attempts >= this.maxAttempts) {
            throw new Error('Max reconnection attempts reached');
        }

        this.attempts++;
        const delay = this.getDelay();

        console.log(`Reconnecting in ${delay}ms (attempt ${this.attempts}/${this.maxAttempts})`);

        await new Promise(resolve => setTimeout(resolve, delay));

        try {
            await connectFunction();
            this.attempts = 0; // Reset on success
        } catch (error) {
            await this.reconnect(connectFunction);
        }
    }
}
```

### 3. Memory Management

```javascript
class WebSocketPool {
    constructor() {
        this.connections = new Map();
    }

    add(key, ws) {
        this.connections.set(key, ws);
    }

    remove(key) {
        const ws = this.connections.get(key);
        if (ws) {
            ws.disconnect();
            this.connections.delete(key);
        }
    }

    disconnectAll() {
        this.connections.forEach(ws => ws.disconnect());
        this.connections.clear();
    }
}

// Usage
const wsPool = new WebSocketPool();

// Add connection
wsPool.add('notifications', notificationWS);

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    wsPool.disconnectAll();
});
```

### 4. Request Browser Notification Permission

```javascript
async function requestNotificationPermission() {
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }
    return false;
}

// Request permission on user interaction
document.querySelector('#enable-notifications')?.addEventListener('click', async () => {
    const granted = await requestNotificationPermission();
    if (granted) {
        console.log('Notification permission granted');
    }
});
```

---

## Complete Integration Example

### React Component Example

```jsx
import React, { useEffect, useState, useCallback } from 'react';
import { NotificationWebSocket } from './websockets';
import { getWebSocketToken } from './api';

function NotificationCenter() {
    const [ws, setWs] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        let websocket;

        const initWebSocket = async () => {
            try {
                // Get token
                const tokenData = await getWebSocketToken();

                // Create WebSocket
                websocket = new NotificationWebSocket(tokenData.token);

                // Set up listeners
                websocket.on('connected', () => {
                    setIsConnected(true);
                });

                websocket.on('disconnected', () => {
                    setIsConnected(false);
                });

                websocket.on('notification', (notification) => {
                    setNotifications(prev => [notification, ...prev]);
                });

                websocket.on('unread_count', (count) => {
                    setUnreadCount(count);
                });

                // Connect
                websocket.connect();
                setWs(websocket);

            } catch (error) {
                console.error('Failed to initialize WebSocket:', error);
            }
        };

        initWebSocket();

        // Cleanup
        return () => {
            if (websocket) {
                websocket.disconnect();
            }
        };
    }, []);

    const handleMarkAsRead = useCallback((notificationId) => {
        if (ws) {
            ws.markAsRead(notificationId);
            setNotifications(prev =>
                prev.map(n =>
                    n.id === notificationId ? { ...n, is_read: true } : n
                )
            );
        }
    }, [ws]);

    const handleMarkAllAsRead = useCallback(() => {
        if (ws) {
            ws.markAllAsRead();
            setNotifications(prev =>
                prev.map(n => ({ ...n, is_read: true }))
            );
        }
    }, [ws]);

    return (
        <div className="notification-center">
            <div className="header">
                <h2>Notifications</h2>
                <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
                    {isConnected ? '● Connected' : '○ Disconnected'}
                </span>
                {unreadCount > 0 && (
                    <span className="badge">{unreadCount}</span>
                )}
            </div>

            {notifications.length > 0 && (
                <button onClick={handleMarkAllAsRead}>
                    Mark All as Read
                </button>
            )}

            <div className="notification-list">
                {notifications.map(notification => (
                    <div
                        key={notification.id}
                        className={`notification-item ${notification.is_read ? 'read' : 'unread'}`}
                        onClick={() => handleMarkAsRead(notification.id)}
                    >
                        <h4>{notification.title}</h4>
                        <p>{notification.message}</p>
                        <small>{new Date(notification.created_at).toLocaleString()}</small>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default NotificationCenter;
```

---

## Testing

### Manual Testing

```javascript
// Test notification WebSocket
const testNotificationWS = async () => {
    const tokenData = await getWebSocketToken();
    const ws = new NotificationWebSocket(tokenData.token);

    ws.on('connected', () => console.log('✅ Connected'));
    ws.on('notification', (n) => console.log('📬 Notification:', n));
    ws.on('unread_count', (c) => console.log('📊 Unread:', c));

    ws.connect();

    // Test ping
    setTimeout(() => ws.ping(), 5000);

    // Test mark as read
    setTimeout(() => {
        ws.markAsRead('some-notification-id');
    }, 10000);
};

testNotificationWS();
```

---

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Django server is running with Channels
   - Check Redis is running
   - Verify WebSocket URL is correct

2. **401 Unauthorized**
   - Token is expired or invalid
   - Get a new token from `/api/realtime/token/`

3. **403 Forbidden**
   - User doesn't have permission
   - Check user authentication
   - Verify user has access to the resource

4. **Connection Drops Frequently**
   - Implement exponential backoff for reconnection
   - Use ping/pong for keep-alive
   - Check network stability

---

## Next Steps

- Implement WebSocket client in your frontend framework
- Add error handling and reconnection logic
- Set up browser notifications
- Test with real-time scenarios
- Monitor WebSocket performance

---

Generated with [Claude Code](https://claude.com/claude-code)
