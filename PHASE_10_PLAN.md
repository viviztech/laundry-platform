# Phase 10: Mobile Application - Implementation Plan

**Duration**: Weeks 20-22 (15-21 days)
**Status**: Planning → In Progress
**Date Started**: January 3, 2026

---

## 📱 Overview

Build a cross-platform mobile application using React Native for both iOS and Android platforms, providing customers and partners with native mobile experience for the LaundryConnect platform.

---

## 🎯 Objectives

1. Create React Native mobile app (iOS + Android)
2. Implement all core features from web platform
3. Add mobile-specific features (camera, GPS, biometric auth)
4. Optimize backend APIs for mobile consumption
5. Prepare for app store deployment

---

## 📋 Phase Breakdown

### Part 1: Project Setup & Configuration (Days 1-2)

#### 1.1 Initialize React Native Project
```bash
npx react-native init LaundryConnectMobile --template react-native-template-typescript
```

**Dependencies to Install**:
```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.73.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4",
    "axios": "^1.6.2",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "react-native-keychain": "^8.1.2",
    "react-native-biometrics": "^3.0.1",
    "react-native-vector-icons": "^10.0.3",
    "@react-native-firebase/app": "^19.0.0",
    "@react-native-firebase/messaging": "^19.0.0",
    "react-native-push-notification": "^8.1.1",
    "socket.io-client": "^4.6.0",
    "react-native-image-picker": "^7.1.0",
    "react-native-maps": "^1.10.0",
    "@react-native-geolocation/geolocation": "^3.0.6",
    "react-native-permissions": "^4.1.0",
    "react-native-dotenv": "^3.4.9",
    "react-native-fast-image": "^8.6.3",
    "react-native-gesture-handler": "^2.14.1",
    "react-native-reanimated": "^3.6.1",
    "react-native-safe-area-context": "^4.8.2",
    "react-native-screens": "^3.29.0",
    "react-native-webview": "^13.6.4",
    "date-fns": "^3.0.6",
    "formik": "^2.4.5",
    "yup": "^1.3.3"
  },
  "devDependencies": {
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

#### 1.2 Project Structure
```
mobile/
├── src/
│   ├── api/              # API client and endpoints
│   ├── assets/           # Images, fonts, icons
│   ├── components/       # Reusable components
│   ├── navigation/       # Navigation configuration
│   ├── screens/          # Screen components
│   │   ├── auth/
│   │   ├── home/
│   │   ├── services/
│   │   ├── orders/
│   │   ├── tracking/
│   │   ├── chat/
│   │   ├── profile/
│   │   └── partner/
│   ├── store/            # Redux store
│   │   ├── slices/
│   │   └── store.ts
│   ├── hooks/            # Custom hooks
│   ├── utils/            # Utility functions
│   ├── constants/        # Constants and config
│   ├── types/            # TypeScript types
│   └── theme/            # Theme configuration
├── android/
├── ios/
└── App.tsx
```

#### 1.3 Configuration Files
- `.env` - Environment variables
- `tsconfig.json` - TypeScript configuration
- `.eslintrc.js` - ESLint rules
- `.prettierrc` - Prettier formatting

---

### Part 2: Core Infrastructure (Days 3-4)

#### 2.1 API Client Setup

**File**: `src/api/client.ts`
```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        // Refresh token logic
      }
    }
    return Promise.reject(error);
  }
);
```

#### 2.2 Redux Store Setup

**File**: `src/store/store.ts`
```typescript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import servicesReducer from './slices/servicesSlice';
import ordersReducer from './slices/ordersSlice';
import notificationsReducer from './slices/notificationsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    services: servicesReducer,
    orders: ordersReducer,
    notifications: notificationsReducer,
  },
});
```

#### 2.3 Navigation Setup

**File**: `src/navigation/AppNavigator.tsx`
- Stack Navigator for auth flow
- Bottom Tab Navigator for main app
- Stack navigators for each tab
- Deep linking configuration

---

### Part 3: Authentication & Onboarding (Days 5-6)

#### 3.1 Screens to Build
1. **Splash Screen** - App loading
2. **Onboarding** - Feature introduction (3-4 slides)
3. **Login Screen** - Email/Phone + Password
4. **Register Screen** - Multi-step registration
5. **OTP Verification** - Phone/Email verification
6. **Biometric Setup** - Face ID/Touch ID/Fingerprint

#### 3.2 Features
- JWT token management
- Biometric authentication
- Social login (Google, Apple)
- Remember me functionality
- Auto-login on app restart
- Secure token storage (Keychain)

#### 3.3 API Endpoints Used
- `POST /api/accounts/register/`
- `POST /api/accounts/login/`
- `POST /api/accounts/verify-otp/`
- `POST /api/accounts/token/refresh/`

---

### Part 4: Home & Services (Days 7-8)

#### 4.1 Home Screen
- User greeting
- Quick actions (New Order, Track Order)
- Active orders summary
- Service categories grid
- Promotional banners
- Recent orders list

#### 4.2 Services Screens
1. **Service Categories** - Browse categories
2. **Service Items** - Items within category
3. **Service Details** - Detailed service info
4. **Pricing Calculator** - Price estimation

#### 4.3 Features
- Category filtering
- Search functionality
- Add to cart
- Price calculation
- Image galleries
- Service ratings

---

### Part 5: Order Management (Days 9-10)

#### 5.1 Screens
1. **New Order** - Create order flow
   - Service selection
   - Garment details
   - Pickup address
   - Delivery address
   - Schedule pickup
   - Order summary
2. **Order History** - Past orders list
3. **Order Details** - Detailed order view
4. **Order Tracking** - Real-time tracking

#### 5.2 Features
- Multi-step order creation
- Address autocomplete
- Date/time picker for scheduling
- Payment integration
- Order status updates
- Cancel order
- Reorder functionality

#### 5.3 Camera Integration
- Take photos of garments
- Upload garment images
- AI garment recognition
- Stain detection

---

### Part 6: Real-time Features (Days 11-12)

#### 6.1 WebSocket Integration

**File**: `src/utils/websocket.ts`
```typescript
import io from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;

  connect(token: string) {
    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket Connected');
    });

    this.socket.on('notification', (data) => {
      // Handle notifications
    });

    this.socket.on('order_update', (data) => {
      // Handle order updates
    });
  }

  disconnect() {
    this.socket?.disconnect();
  }
}
```

#### 6.2 Live Tracking
- Google Maps integration
- Partner location on map
- Route visualization
- ETA display
- Location permissions

#### 6.3 Push Notifications
- Firebase Cloud Messaging setup
- Notification permissions
- Local notifications
- Badge count management
- Notification actions

---

### Part 7: Chat & Support (Day 13)

#### 7.1 Chat Screen
- Message list with auto-scroll
- Text input with send button
- Image sharing
- Typing indicators
- Read receipts
- Timestamp display

#### 7.2 WebSocket Chat
```typescript
socket.emit('chat_message', {
  room_id: orderId,
  message: text,
});

socket.on('new_message', (message) => {
  // Update chat UI
});
```

---

### Part 8: Payment Integration (Day 14)

#### 8.1 Payment Screens
1. **Payment Methods** - List saved methods
2. **Add Payment Method** - Add new card/UPI
3. **Wallet** - View balance, add money
4. **Payment Gateway** - Razorpay/Stripe WebView

#### 8.2 Features
- Save payment methods
- Wallet integration
- Multiple payment gateways
- Payment history
- Refund status

---

### Part 9: Profile & Settings (Day 15)

#### 9.1 Profile Screens
1. **Profile View** - User info display
2. **Edit Profile** - Update user details
3. **Addresses** - Manage addresses
4. **Notification Preferences** - Settings
5. **Payment Methods** - Saved methods
6. **About** - App info, terms, privacy

#### 9.2 Features
- Profile photo upload
- Form validation
- Address CRUD
- Notification toggles
- Dark mode support
- Language selection

---

### Part 10: Partner App Features (Day 16)

#### 10.1 Partner Screens
1. **Partner Dashboard** - Orders, earnings
2. **Pending Orders** - Accept/reject
3. **Active Orders** - In-progress orders
4. **Order Details** - Partner view
5. **Earnings** - Revenue tracking
6. **Performance** - Metrics and ratings

#### 10.2 Features
- Accept/reject orders
- Update order status
- Upload completion photos
- Navigate to customer location
- Earnings summary

---

### Part 11: Mobile-Specific Features (Days 17-18)

#### 11.1 Camera Features
```typescript
import {launchCamera, launchImageLibrary} from 'react-native-image-picker';

const takePhoto = async () => {
  const result = await launchCamera({
    mediaType: 'photo',
    quality: 0.8,
    includeBase64: false,
  });

  if (result.assets?.[0]) {
    uploadImage(result.assets[0].uri);
  }
};
```

#### 11.2 GPS & Location
```typescript
import Geolocation from '@react-native-geolocation/geolocation';

Geolocation.getCurrentPosition(
  (position) => {
    const {latitude, longitude} = position.coords;
    updateLocation(latitude, longitude);
  },
  (error) => console.error(error),
  {enableHighAccuracy: true, timeout: 15000}
);
```

#### 11.3 Offline Mode
- Cache API responses
- Local data persistence
- Sync when online
- Offline indicator

#### 11.4 Deep Linking
```typescript
// Handle deep links
const config = {
  screens: {
    OrderDetails: 'order/:orderId',
    ServiceDetails: 'service/:serviceId',
  },
};
```

---

### Part 12: Performance Optimization (Day 19)

#### 12.1 Image Optimization
```typescript
import FastImage from 'react-native-fast-image';

<FastImage
  source={{uri: imageUrl, priority: FastImage.priority.normal}}
  resizeMode={FastImage.resizeMode.cover}
  style={{width: 200, height: 200}}
/>
```

#### 12.2 List Optimization
- FlatList with `windowSize` optimization
- Memoization with `React.memo`
- `useMemo` and `useCallback` hooks
- Lazy loading images

#### 12.3 Bundle Optimization
- Code splitting
- Remove unused imports
- Optimize images
- Enable Hermes engine

---

### Part 13: Backend API Optimization (Day 20)

#### 13.1 New Mobile-Optimized Endpoints

**File**: `apps/mobile/views.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def mobile_dashboard(request):
    """Optimized dashboard for mobile app"""
    return Response({
        'user': UserSerializer(request.user).data,
        'active_orders': Order.objects.filter(
            user=request.user,
            status__in=['pending', 'confirmed', 'in_progress']
        ).count(),
        'recent_orders': OrderSerializer(
            Order.objects.filter(user=request.user)[:5],
            many=True
        ).data,
        'wallet_balance': request.user.wallet.balance,
        'notifications_count': request.user.notifications.filter(
            is_read=False
        ).count(),
    })

@api_view(['POST'])
def upload_garment_image(request):
    """Handle garment image uploads with compression"""
    image = request.FILES.get('image')
    # Image processing and AI recognition
    pass
```

#### 13.2 API Improvements
- Add pagination to all list endpoints
- Implement field filtering (`?fields=id,name`)
- Add response compression (gzip)
- Optimize database queries
- Add caching headers

**File**: `apps/mobile/serializers.py`
```python
class MobileDashboardSerializer(serializers.Serializer):
    """Lightweight serializer for mobile"""
    class Meta:
        fields = ['id', 'name', 'status', 'total']  # Minimal fields
```

---

### Part 14: Testing & Quality (Day 21)

#### 14.1 Testing Strategy
1. **Unit Tests** - Component testing
2. **Integration Tests** - API integration
3. **E2E Tests** - User flow testing
4. **Performance Tests** - Load testing

#### 14.2 Tools
- Jest for unit tests
- React Native Testing Library
- Detox for E2E testing
- Flipper for debugging

---

## 🛠️ Backend Changes Required

### New Django App: `mobile`

```bash
python manage.py startapp mobile
```

**Models**: None (uses existing models)

**Views**: Mobile-optimized endpoints
- `mobile_dashboard/` - Dashboard data
- `mobile_services/` - Optimized service list
- `mobile_orders/` - Optimized order list
- `upload_image/` - Image upload with compression

**Settings Changes**:
```python
# config/settings/base.py
INSTALLED_APPS += ['apps.mobile']

# Image upload settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

# CORS for mobile
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8081',  # React Native Metro
]
```

---

## 📱 App Store Preparation

### iOS App Store

1. **Requirements**:
   - Apple Developer Account ($99/year)
   - App icons (all sizes)
   - Screenshots (all device sizes)
   - App description
   - Privacy policy URL
   - Terms of service URL

2. **Build Process**:
```bash
cd ios
pod install
xcodebuild -workspace LaundryConnect.xcworkspace -scheme LaundryConnect archive
```

3. **TestFlight**:
   - Upload to App Store Connect
   - Internal testing
   - External testing
   - Beta feedback

### Android Play Store

1. **Requirements**:
   - Google Play Developer Account ($25 one-time)
   - App icons
   - Screenshots
   - Feature graphic
   - App description
   - Privacy policy URL

2. **Build Process**:
```bash
cd android
./gradlew bundleRelease
```

3. **Testing**:
   - Internal testing track
   - Closed testing
   - Open testing
   - Production rollout

---

## 📊 Success Criteria

### Functional Requirements
- [ ] User can register and login
- [ ] Biometric authentication works
- [ ] User can browse services
- [ ] User can create orders
- [ ] Real-time order tracking
- [ ] Push notifications working
- [ ] In-app chat functional
- [ ] Payment integration complete
- [ ] Camera features working
- [ ] GPS tracking functional
- [ ] Offline mode operational
- [ ] Partner features complete

### Performance Requirements
- [ ] App launches in < 3 seconds
- [ ] Smooth 60 FPS scrolling
- [ ] API responses < 2 seconds
- [ ] Images load progressively
- [ ] App size < 50MB
- [ ] Battery efficient

### Quality Requirements
- [ ] No crashes
- [ ] 90%+ test coverage
- [ ] Accessible (WCAG 2.1)
- [ ] Works on iOS 13+ and Android 8+
- [ ] Supports tablets
- [ ] Dark mode support

---

## 📁 Deliverables

1. **Mobile App**:
   - ✅ React Native codebase
   - ✅ iOS app (TestFlight ready)
   - ✅ Android app (Play Store ready)

2. **Backend Updates**:
   - ✅ Mobile API endpoints
   - ✅ Image optimization
   - ✅ API documentation

3. **Documentation**:
   - ✅ Setup guide
   - ✅ API documentation
   - ✅ User manual
   - ✅ Store listing assets

4. **Testing**:
   - ✅ Test suite
   - ✅ Test reports
   - ✅ Performance benchmarks

---

## 🗓️ Timeline

| Day | Tasks |
|-----|-------|
| 1-2 | Project setup, dependencies, configuration |
| 3-4 | API client, Redux, navigation |
| 5-6 | Authentication screens, biometric |
| 7-8 | Home screen, services browsing |
| 9-10 | Order management, camera |
| 11-12 | WebSocket, tracking, notifications |
| 13 | Chat implementation |
| 14 | Payment integration |
| 15 | Profile and settings |
| 16 | Partner features |
| 17-18 | Mobile features, optimization |
| 19 | Performance tuning |
| 20 | Backend optimization |
| 21 | Testing, bug fixes |

---

## 🚀 Next Steps

1. ✅ Create mobile project directory
2. ✅ Initialize React Native project
3. ✅ Install dependencies
4. ✅ Set up project structure
5. ✅ Configure navigation
6. ✅ Build authentication flow
7. ✅ Implement core features
8. ✅ Add mobile-specific features
9. ✅ Optimize and test
10. ✅ Prepare for store submission

---

**Phase 10 Status**: 🚀 Ready to Start

**Document Created**: January 3, 2026
**Last Updated**: January 3, 2026
