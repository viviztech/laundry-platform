# LaundryConnect Mobile Apps Guide
**Customer & Partner Apps - React Native**

---

## 📱 Overview

LaundryConnect has a unified React Native codebase that serves **both Customer and Partner apps** through role-based navigation and features.

### **Technology Stack:**
- **Framework**: React Native (Expo)
- **Navigation**: React Navigation (Stack & Tabs)
- **State Management**: Redux Toolkit
- **API Client**: Axios with JWT auth
- **Real-time**: Socket.IO
- **Notifications**: Expo Notifications
- **Forms**: Formik + Yup validation

---

## 🚀 Quick Start

### **Prerequisites:**
```bash
# Install Node.js (v18+)
node --version

# Install Expo CLI globally
npm install -g expo-cli

# Install dependencies
cd mobile
npm install
```

### **Run the App:**
```bash
# Start Expo dev server
npm start

# Or run specific platform
npm run android  # Android emulator
npm run ios      # iOS simulator
npm run web      # Web browser
```

### **Backend Connection:**
Update API endpoint in `mobile/src/constants/api.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api',  // Your Django server
  TIMEOUT: 30000,
  UPLOAD_TIMEOUT: 60000,
};
```

---

## 👤 Customer App Features

### **Core Screens:**

#### **1. Authentication** 🔐
- **LoginScreen** - Email/password login
- **RegisterScreen** - Customer signup
- **SplashScreen** - App initialization

**API Endpoints:**
```
POST /api/accounts/register/
POST /api/accounts/login/
POST /api/accounts/token/refresh/
GET  /api/accounts/profile/
```

#### **2. Home Screen** 🏠
- Service categories display
- Featured services
- Quick order access
- Active orders summary

**Features:**
- Browse all service categories
- View service prices
- Quick reorder from history
- See current order status

#### **3. Services** 🧺
- **ServicesScreen** - Service catalog by category
- **ServiceDetailScreen** - Detailed service info with pricing

**API Endpoints:**
```
GET /api/services/categories/
GET /api/services/
GET /api/services/{id}/
GET /api/services/pricing/?zone=<zone>
```

#### **4. Orders** 📦
- **NewOrderScreen** - Create new order
- **OrdersScreen** - Order history
- **OrderDetailScreen** - Track order status

**Features:**
- Add items to cart
- Select pickup/delivery address
- Choose pickup/delivery dates
- Real-time order tracking
- Chat with partner

**Order Flow:**
1. Select services and quantities
2. Choose addresses
3. Select delivery date
4. Review and confirm
5. Make payment
6. Track order

**API Endpoints:**
```
POST /api/orders/
GET  /api/orders/
GET  /api/orders/{id}/
PATCH /api/orders/{id}/
GET  /api/orders/{id}/track/
```

#### **5. Profile** 👨‍💼
- **ProfileScreen** - User settings
- **AddressListScreen** - Manage addresses
- **AddEditAddressScreen** - Add/edit address

**Features:**
- Update profile info
- Manage delivery addresses
- Set notification preferences
- View order history

**API Endpoints:**
```
GET  /api/accounts/profile/
PATCH /api/accounts/profile/
GET  /api/accounts/addresses/
POST /api/accounts/addresses/
PATCH /api/accounts/addresses/{id}/
DELETE /api/accounts/addresses/{id}/
```

#### **6. Payment** 💳
- **WalletScreen** - Wallet balance & topup
- **PaymentMethodsScreen** - Saved payment methods
- **PaymentGatewayScreen** - Payment processing

**Features:**
- Wallet topup
- Save payment methods
- Payment history
- Transaction details

**API Endpoints:**
```
GET  /api/payments/wallet/
POST /api/payments/wallet/topup/
GET  /api/payments/methods/
POST /api/payments/methods/
GET  /api/payments/transactions/
POST /api/payments/process/
```

#### **7. Chat** 💬
- **ChatListScreen** - All conversations
- **ChatScreen** - Chat with partner

**Features:**
- Real-time messaging with partners
- Order-specific chats
- Message history
- Typing indicators

**API Endpoints:**
```
GET  /api/chat/rooms/
GET  /api/chat/rooms/{id}/messages/
POST /api/chat/rooms/{id}/messages/
WebSocket: ws://localhost:8000/ws/chat/{room_id}/
```

---

## 🏢 Partner App Features

### **Core Screens:**

#### **1. Dashboard** 📊
- Today's orders count
- Pending orders
- Revenue summary
- Quick actions

**Features:**
- View daily statistics
- See pending orders requiring action
- Quick access to common tasks
- Earnings overview

#### **2. Orders Management** 📋
- View assigned orders
- Update order status
- See order details
- Communicate with customers

**Order Statuses Partner Can Update:**
```
pending → confirmed (Accept order)
confirmed → picked_up (Mark as picked up)
picked_up → in_progress (Start processing)
in_progress → ready (Mark as ready)
ready → out_for_delivery (Start delivery)
out_for_delivery → delivered (Mark as delivered)
```

**API Endpoints:**
```
GET  /api/partners/orders/assigned/
PATCH /api/partners/orders/{id}/status/
GET  /api/partners/orders/{id}/
```

#### **3. Availability Management** ⏰
- Set working hours
- Mark holidays
- Update capacity
- Quick on/off toggle

**Features:**
- Set daily schedules
- Manage holidays
- Update daily capacity
- Temporarily close business

**API Endpoints:**
```
GET  /api/partners/profile/
PATCH /api/partners/availability/
POST /api/partners/holidays/
GET  /api/partners/capacity/
```

#### **4. Earnings & Payments** 💰
- Today's earnings
- Weekly/monthly revenue
- Payment history
- Pending settlements

**API Endpoints:**
```
GET /api/partners/earnings/
GET /api/partners/payments/
GET /api/partners/settlements/
```

#### **5. Profile & Business** 🏪
- Business information
- Service areas
- Bank details
- Documents

**API Endpoints:**
```
GET  /api/partners/profile/
PATCH /api/partners/profile/
GET  /api/partners/service-areas/
PATCH /api/partners/service-areas/
```

---

## 📂 Mobile App Structure

```
mobile/
├── src/
│   ├── api/                    # API integration
│   │   ├── client.ts          # Axios client with auth
│   │   └── endpoints/         # API endpoint definitions
│   │
│   ├── screens/               # All app screens
│   │   ├── auth/             # Login, Register, Splash
│   │   ├── home/             # Home screen
│   │   ├── services/         # Service catalog
│   │   ├── orders/           # Order management
│   │   ├── profile/          # User profile & settings
│   │   ├── payment/          # Payments & wallet
│   │   ├── chat/             # Messaging
│   │   ├── partner/          # Partner-specific screens
│   │   └── tracking/         # Real-time tracking
│   │
│   ├── components/            # Reusable components
│   │   ├── common/           # Buttons, inputs, cards
│   │   ├── orders/           # Order-related components
│   │   └── layout/           # Layout components
│   │
│   ├── navigation/            # Navigation setup
│   │   └── AppNavigator.tsx  # Main navigation
│   │
│   ├── store/                 # Redux state management
│   │   ├── store.ts          # Redux store config
│   │   └── slices/           # Redux slices
│   │       ├── authSlice.ts
│   │       ├── orderSlice.ts
│   │       ├── paymentSlice.ts
│   │       └── chatSlice.ts
│   │
│   ├── services/              # Business logic
│   │   ├── authService.ts
│   │   ├── orderService.ts
│   │   └── socketService.ts   # WebSocket for real-time
│   │
│   ├── utils/                 # Helper functions
│   ├── types/                 # TypeScript types
│   ├── constants/             # App constants
│   └── theme/                 # Styling & theming
│
├── assets/                    # Images, fonts
├── App.tsx                    # App entry point
└── package.json
```

---

## 🔌 API Integration

### **Authentication Flow:**

```typescript
// Login
const response = await apiClient.post('/accounts/login/', {
  email: 'user@example.com',
  password: 'password123'
});

// Store tokens
await apiClient.setTokens(response.data.access, response.data.refresh);

// API calls automatically include auth token
const orders = await apiClient.get('/orders/');
```

### **Redux State Management:**

```typescript
// Dispatch action
dispatch(login({ email, password }));

// Access state
const { user, isAuthenticated } = useSelector((state) => state.auth);
const { orders, loading } = useSelector((state) => state.orders);
```

### **Real-time Updates (WebSocket):**

```typescript
// Connect to WebSocket
socketService.connect(roomId);

// Listen for messages
socketService.on('new_message', (message) => {
  dispatch(addMessage(message));
});

// Send message
socketService.emit('send_message', { text: 'Hello!' });
```

---

## 🎨 Key Features Implemented

### **✅ Customer App:**
- [x] User authentication (Login/Register)
- [x] Browse services by category
- [x] Create new orders
- [x] View order history
- [x] Track orders in real-time
- [x] Manage delivery addresses
- [x] Wallet & payments
- [x] Chat with partners
- [x] Push notifications

### **✅ Partner App:**
- [x] Partner authentication
- [x] View assigned orders
- [x] Update order status
- [x] Manage availability
- [x] View earnings
- [x] Chat with customers
- [x] Business profile management

---

## 🔔 Push Notifications Setup

### **Configure Expo Notifications:**

```bash
# Install expo-notifications (already in package.json)
expo install expo-notifications expo-device
```

### **Request Permission & Get Token:**

```typescript
import * as Notifications from 'expo-notifications';

// Request permission
const { status } = await Notifications.requestPermissionsAsync();

// Get push token
const token = await Notifications.getExpoPushTokenAsync();

// Send token to backend
await apiClient.post('/notifications/register-device/', {
  token: token.data,
  platform: Platform.OS
});
```

### **Handle Notifications:**

```typescript
// Listen for notifications
Notifications.addNotificationReceivedListener((notification) => {
  console.log('Notification received:', notification);
});

Notifications.addNotificationResponseReceivedListener((response) => {
  // Handle notification tap
  const { data } = response.notification.request.content;
  if (data.orderId) {
    navigation.navigate('OrderDetail', { id: data.orderId });
  }
});
```

---

## 🧪 Testing

### **Test Accounts:**

**Customer:**
```
Email: demo.customer@test.com
Password: demo123
```

**Partner:**
```
Email: cleanpro@business.com
Password: partner123
```

### **Test Scenarios:**

#### **Customer Flow:**
1. Login as customer
2. Browse services
3. Create new order
4. Select items (2-3 services)
5. Choose address
6. Complete payment
7. Track order status
8. Chat with partner

#### **Partner Flow:**
1. Login as partner
2. View assigned orders
3. Accept pending order
4. Update order status step by step
5. Chat with customer
6. Mark order as delivered
7. View earnings

---

## 🚀 Build & Deploy

### **Build for Production:**

```bash
# Android
expo build:android

# iOS
expo build:ios

# Or use EAS Build (recommended)
eas build --platform android
eas build --platform ios
```

### **Environment Configuration:**

Create `.env` file:
```
API_BASE_URL=https://api.laundryconnect.com
SOCKET_URL=wss://api.laundryconnect.com
RAZORPAY_KEY=your_razorpay_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

---

## 📊 Features Priority for Launch

### **Must Have (Implemented):** ⭐⭐⭐
- ✅ Authentication
- ✅ Service browsing
- ✅ Order creation & tracking
- ✅ Basic payments
- ✅ Chat functionality
- ✅ Address management
- ✅ Partner order management

### **Should Have (Add Soon):** ⭐⭐
- ⏳ Order ratings & reviews
- ⏳ Promotional offers
- ⏳ Referral program
- ⏳ Advanced notifications
- ⏳ Order scheduling (future dates)

### **Nice to Have (Later):** ⭐
- ⏳ AI-based price estimation
- ⏳ Subscription plans
- ⏳ Loyalty points
- ⏳ In-app camera for garment detection

---

## 🔧 Configuration Files

### **API Configuration** (`src/constants/api.ts`):
```typescript
export const API_CONFIG = {
  BASE_URL: __DEV__
    ? 'http://localhost:8000/api'  // Development
    : 'https://api.laundryconnect.com/api',  // Production
  TIMEOUT: 30000,
  UPLOAD_TIMEOUT: 60000,
};

export const SOCKET_CONFIG = {
  URL: __DEV__
    ? 'http://localhost:8000'
    : 'https://api.laundryconnect.com',
};
```

### **App Configuration** (`app.json`):
```json
{
  "expo": {
    "name": "LaundryConnect",
    "slug": "laundryconnect",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.laundryconnect.mobile"
    },
    "android": {
      "package": "com.laundryconnect.mobile"
    }
  }
}
```

---

## 📱 Screen Flow Diagrams

### **Customer Order Flow:**
```
Splash → Login → Home
                   ↓
          Browse Services
                   ↓
          Service Detail → Add to Cart
                   ↓
          New Order (Cart)
                   ↓
          Select Addresses
                   ↓
          Choose Date & Time
                   ↓
          Review Order
                   ↓
          Payment
                   ↓
          Order Confirmation
                   ↓
          Track Order ← Chat with Partner
```

### **Partner Order Flow:**
```
Login → Dashboard → View Orders
                        ↓
                    Order Detail
                        ↓
                Accept/Confirm
                        ↓
                Update Status
                (picked_up → in_progress → ready)
                        ↓
                Out for Delivery
                        ↓
                Mark Delivered
                        ↓
                View Earnings
```

---

## 🐛 Troubleshooting

### **Common Issues:**

**Issue: "Network Error" when calling API**
```typescript
// Solution: Check API_BASE_URL in constants/api.ts
// For Android emulator use: http://10.0.2.2:8000/api
// For iOS simulator use: http://localhost:8000/api
```

**Issue: "Unauthorized" errors**
```typescript
// Solution: Token might be expired or invalid
// Clear AsyncStorage and login again
await AsyncStorage.clear();
```

**Issue: WebSocket not connecting**
```typescript
// Solution: Ensure Django Channels is configured
// Check SOCKET_URL matches backend WebSocket endpoint
```

---

## 📚 Next Steps

1. **Test Both Apps Thoroughly**
   - Customer journey end-to-end
   - Partner order processing
   - Real-time features (chat, tracking)

2. **Add Missing Features**
   - Order ratings
   - Push notifications
   - Advanced filters

3. **Optimize Performance**
   - Image optimization
   - API response caching
   - Lazy loading

4. **Prepare for Production**
   - Update environment variables
   - Configure payment gateways
   - Set up analytics
   - Create app store assets

---

**Ready to launch!** 🚀

Both Customer and Partner apps are functional and ready for testing with your backend API.

---

**Last Updated**: January 12, 2026
**Version**: 1.0.0 - Partner Launch Edition
