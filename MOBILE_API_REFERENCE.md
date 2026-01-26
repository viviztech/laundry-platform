# Mobile App API Reference
**Backend API Endpoints for Customer & Partner Apps**

---

## 🔐 Authentication Endpoints

### **Register New User**
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210",
  "user_type": "customer"  // or "partner"
}

Response 201:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "customer"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **Login**
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "user_type": "customer"
  }
}
```

### **Refresh Token**
```http
POST /api/accounts/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **Get Current User Profile**
```http
GET /api/accounts/profile/
Authorization: Bearer {access_token}

Response 200:
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210",
  "user_type": "customer",
  "is_verified": true
}
```

---

## 📍 Address Management (Customer)

### **List Addresses**
```http
GET /api/accounts/addresses/
Authorization: Bearer {access_token}

Response 200:
[
  {
    "id": "uuid",
    "address_type": "home",
    "address_line1": "123 Main Street",
    "address_line2": "Indiranagar",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560038",
    "latitude": 12.9716,
    "longitude": 77.6412,
    "is_default": true
  }
]
```

### **Create Address**
```http
POST /api/accounts/addresses/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "address_type": "home",  // home, work, other
  "address_line1": "123 Main Street",
  "address_line2": "Indiranagar",
  "city": "Bangalore",
  "state": "Karnataka",
  "pincode": "560038",
  "latitude": 12.9716,
  "longitude": 77.6412,
  "is_default": false
}

Response 201: {address object}
```

### **Update Address**
```http
PATCH /api/accounts/addresses/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_default": true
}

Response 200: {updated address}
```

### **Delete Address**
```http
DELETE /api/accounts/addresses/{id}/
Authorization: Bearer {access_token}

Response 204: No Content
```

---

## 🧺 Services & Catalog

### **List Service Categories**
```http
GET /api/services/categories/

Response 200:
[
  {
    "id": "uuid",
    "name": "Wash & Iron",
    "slug": "wash-iron",
    "description": "Complete washing and ironing service",
    "icon": "wash_iron",
    "is_active": true
  }
]
```

### **List Services**
```http
GET /api/services/?category={category_id}&zone={zone}
Optional query params:
  - category: Filter by category ID
  - zone: Pricing zone (A, B, C)
  - is_active: true/false

Response 200:
[
  {
    "id": "uuid",
    "name": "Wash & Iron - Shirt",
    "category": {
      "id": "uuid",
      "name": "Wash & Iron"
    },
    "garment": {
      "id": "uuid",
      "name": "Shirt"
    },
    "description": "Professional washing and ironing",
    "turnaround_time": "standard",
    "pricing": [
      {
        "zone": "A",
        "base_price": "36.00",
        "discount_price": "30.00"
      }
    ]
  }
]
```

### **Get Service Detail**
```http
GET /api/services/{id}/?zone={zone}

Response 200:
{
  "id": "uuid",
  "name": "Wash & Iron - Shirt",
  "description": "...",
  "category": {...},
  "garment": {...},
  "turnaround_time": "standard",
  "pricing_for_zone": {
    "zone": "A",
    "base_price": "36.00",
    "discount_price": "30.00"
  }
}
```

---

## 📦 Orders (Customer)

### **Create New Order**
```http
POST /api/orders/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "pickup_address": "address_uuid",
  "delivery_address": "address_uuid",
  "pickup_date": "2026-01-15T10:00:00Z",
  "delivery_date": "2026-01-17T18:00:00Z",
  "payment_method": "online",  // online, cod, wallet
  "special_instructions": "Handle with care",
  "items": [
    {
      "service": "service_uuid",
      "quantity": 3
    },
    {
      "service": "service_uuid_2",
      "quantity": 2
    }
  ]
}

Response 201:
{
  "id": "uuid",
  "order_number": "ORD202601001",
  "status": "pending",
  "customer": {...},
  "partner": null,
  "items": [...],
  "subtotal": "250.00",
  "delivery_fee": "50.00",
  "tax_amount": "45.00",
  "total_amount": "345.00",
  "payment_status": "pending"
}
```

### **List Orders**
```http
GET /api/orders/?status={status}&page={page}
Authorization: Bearer {access_token}

Optional query params:
  - status: pending, confirmed, picked_up, in_progress, ready, delivered, completed, cancelled
  - page: Page number
  - page_size: Results per page

Response 200:
{
  "count": 25,
  "next": "http://api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "order_number": "ORD202601001",
      "status": "in_progress",
      "total_amount": "345.00",
      "created_at": "2026-01-12T10:00:00Z",
      "partner": {
        "id": "uuid",
        "business_name": "CleanPro Laundry"
      }
    }
  ]
}
```

### **Get Order Detail**
```http
GET /api/orders/{id}/
Authorization: Bearer {access_token}

Response 200:
{
  "id": "uuid",
  "order_number": "ORD202601001",
  "status": "in_progress",
  "customer": {...},
  "partner": {...},
  "pickup_address": {...},
  "delivery_address": {...},
  "items": [
    {
      "service": {...},
      "quantity": 3,
      "unit_price": "30.00",
      "total_price": "90.00"
    }
  ],
  "subtotal": "250.00",
  "delivery_fee": "50.00",
  "tax_amount": "45.00",
  "total_amount": "345.00",
  "payment_method": "online",
  "payment_status": "paid",
  "created_at": "2026-01-12T10:00:00Z",
  "status_history": [
    {
      "status": "pending",
      "timestamp": "2026-01-12T10:00:00Z"
    },
    {
      "status": "confirmed",
      "timestamp": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### **Track Order**
```http
GET /api/orders/{id}/track/
Authorization: Bearer {access_token}

Response 200:
{
  "order_id": "uuid",
  "current_status": "in_progress",
  "timeline": [
    {
      "status": "pending",
      "label": "Order Placed",
      "completed": true,
      "timestamp": "2026-01-12T10:00:00Z"
    },
    {
      "status": "confirmed",
      "label": "Order Confirmed",
      "completed": true,
      "timestamp": "2026-01-12T10:30:00Z"
    },
    {
      "status": "picked_up",
      "label": "Items Picked Up",
      "completed": true,
      "timestamp": "2026-01-12T14:00:00Z"
    },
    {
      "status": "in_progress",
      "label": "Being Processed",
      "completed": true,
      "timestamp": "2026-01-12T15:00:00Z"
    },
    {
      "status": "ready",
      "label": "Ready for Delivery",
      "completed": false,
      "timestamp": null
    }
  ]
}
```

---

## 🏢 Partner Endpoints

### **Get Partner Profile**
```http
GET /api/partners/profile/
Authorization: Bearer {partner_access_token}

Response 200:
{
  "id": "uuid",
  "business_name": "CleanPro Laundry",
  "business_type": "company",
  "contact_person": "Ramesh Kumar",
  "contact_email": "cleanpro@business.com",
  "contact_phone": "+919100000001",
  "address": {...},
  "pricing_zone": "A",
  "service_radius": "5.00",
  "daily_capacity": 100,
  "current_load": 35,
  "status": "active",
  "is_verified": true,
  "average_rating": "4.75",
  "total_ratings": 150,
  "completed_orders": 450
}
```

### **List Assigned Orders**
```http
GET /api/partners/orders/assigned/?status={status}
Authorization: Bearer {partner_access_token}

Response 200:
[
  {
    "id": "uuid",
    "order_number": "ORD202601001",
    "status": "confirmed",
    "customer": {
      "name": "John Doe",
      "phone": "+919876543210"
    },
    "pickup_address": {...},
    "delivery_address": {...},
    "total_amount": "345.00",
    "created_at": "2026-01-12T10:00:00Z"
  }
]
```

### **Update Order Status**
```http
PATCH /api/partners/orders/{id}/status/
Authorization: Bearer {partner_access_token}
Content-Type: application/json

{
  "status": "picked_up",  // confirmed, picked_up, in_progress, ready, out_for_delivery, delivered
  "notes": "Items collected at 2 PM"
}

Response 200:
{
  "id": "uuid",
  "status": "picked_up",
  "updated_at": "2026-01-12T14:00:00Z"
}
```

### **Get Partner Availability**
```http
GET /api/partners/availability/
Authorization: Bearer {partner_access_token}

Response 200:
[
  {
    "weekday": 0,  // 0=Monday, 6=Sunday
    "is_available": true,
    "start_time": "09:00:00",
    "end_time": "21:00:00"
  }
]
```

### **Update Availability**
```http
PATCH /api/partners/availability/
Authorization: Bearer {partner_access_token}
Content-Type: application/json

{
  "weekday": 0,
  "is_available": true,
  "start_time": "09:00:00",
  "end_time": "21:00:00"
}

Response 200: {updated availability}
```

### **Get Earnings**
```http
GET /api/partners/earnings/?period={period}
Authorization: Bearer {partner_access_token}

Query params:
  - period: today, week, month, year

Response 200:
{
  "period": "today",
  "total_orders": 12,
  "completed_orders": 10,
  "gross_revenue": "4500.00",
  "commission_paid": "675.00",
  "net_revenue": "3825.00",
  "pending_settlement": "1200.00"
}
```

---

## 💳 Payments

### **Get Wallet Balance**
```http
GET /api/payments/wallet/
Authorization: Bearer {access_token}

Response 200:
{
  "balance": "450.00",
  "currency": "INR"
}
```

### **Wallet Topup**
```http
POST /api/payments/wallet/topup/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "amount": "500.00",
  "payment_method": "razorpay",
  "payment_details": {...}
}

Response 200:
{
  "transaction_id": "uuid",
  "amount": "500.00",
  "new_balance": "950.00",
  "status": "completed"
}
```

### **Process Payment**
```http
POST /api/payments/process/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "order_id": "order_uuid",
  "payment_method": "online",  // online, cod, wallet
  "payment_gateway": "razorpay",
  "transaction_id": "razorpay_txn_id",
  "amount": "345.00"
}

Response 200:
{
  "payment_id": "uuid",
  "status": "completed",
  "order_id": "order_uuid",
  "amount": "345.00"
}
```

---

## 💬 Chat

### **List Chat Rooms**
```http
GET /api/chat/rooms/
Authorization: Bearer {access_token}

Response 200:
[
  {
    "id": "uuid",
    "order": {
      "id": "uuid",
      "order_number": "ORD202601001"
    },
    "customer": {...},
    "partner": {...},
    "last_message": {
      "text": "Order will be delivered by 6 PM",
      "created_at": "2026-01-12T15:30:00Z"
    },
    "unread_count": 2,
    "is_active": true
  }
]
```

### **Get Chat Messages**
```http
GET /api/chat/rooms/{room_id}/messages/?page={page}
Authorization: Bearer {access_token}

Response 200:
{
  "count": 50,
  "results": [
    {
      "id": "uuid",
      "sender": {
        "id": "uuid",
        "name": "John Doe"
      },
      "message": "Hello, when will you pick up?",
      "created_at": "2026-01-12T14:00:00Z",
      "is_read": true
    }
  ]
}
```

### **Send Message**
```http
POST /api/chat/rooms/{room_id}/messages/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "We'll pick up by 2 PM today"
}

Response 201:
{
  "id": "uuid",
  "sender": {...},
  "message": "We'll pick up by 2 PM today",
  "created_at": "2026-01-12T14:05:00Z",
  "is_read": false
}
```

---

## 🔔 Notifications

### **Register Device for Push Notifications**
```http
POST /api/notifications/register-device/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "token": "ExponentPushToken[xxxxxx]",
  "platform": "android",  // android, ios
  "device_name": "Samsung Galaxy S21"
}

Response 201:
{
  "id": "uuid",
  "token": "ExponentPushToken[xxxxxx]",
  "is_active": true
}
```

### **Get Notification Preferences**
```http
GET /api/notifications/preferences/
Authorization: Bearer {access_token}

Response 200:
{
  "order_updates_email": true,
  "order_updates_push": true,
  "payment_updates_email": true,
  "payment_updates_push": true,
  "marketing_emails": false,
  "promotional_push": false
}
```

### **Update Notification Preferences**
```http
PATCH /api/notifications/preferences/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "order_updates_push": true,
  "marketing_emails": false
}

Response 200: {updated preferences}
```

---

## 🌐 WebSocket Endpoints

### **Chat WebSocket**
```
ws://localhost:8000/ws/chat/{room_id}/?token={access_token}

Client → Server:
{
  "type": "send_message",
  "message": "Hello!"
}

Server → Client:
{
  "type": "new_message",
  "data": {
    "id": "uuid",
    "sender": {...},
    "message": "Hello!",
    "created_at": "2026-01-12T14:00:00Z"
  }
}

Server → Client (Typing):
{
  "type": "user_typing",
  "user": {
    "id": "uuid",
    "name": "John Doe"
  }
}
```

### **Order Tracking WebSocket**
```
ws://localhost:8000/ws/order/{order_id}/?token={access_token}

Server → Client:
{
  "type": "status_update",
  "order_id": "uuid",
  "status": "picked_up",
  "timestamp": "2026-01-12T14:00:00Z"
}

Server → Client (Location Update):
{
  "type": "location_update",
  "latitude": 12.9716,
  "longitude": 77.6412,
  "timestamp": "2026-01-12T14:05:00Z"
}
```

---

## 📊 API Response Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Success, no content to return
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

---

## 🔒 Authentication

All authenticated endpoints require:
```
Authorization: Bearer {access_token}
```

Token expires in 24 hours. Use refresh token to get new access token.

---

**API Documentation:** http://localhost:8000/api/docs/

**Last Updated:** January 12, 2026
