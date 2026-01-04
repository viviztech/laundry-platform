/**
 * API Configuration Constants
 * LaundryConnect Mobile App
 */

export const API_CONFIG = {
  // Base URLs - Update these for production
  BASE_URL: __DEV__ ? 'http://localhost:8000/api' : 'https://api.laundryconnect.com/api',
  WS_URL: __DEV__ ? 'ws://localhost:8000/ws' : 'wss://api.laundryconnect.com/ws',

  // Timeouts
  TIMEOUT: 30000,
  UPLOAD_TIMEOUT: 60000,

  // API Versions
  VERSION: 'v1',
};

export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    REGISTER: '/accounts/auth/register/',
    LOGIN: '/accounts/auth/login/',
    LOGOUT: '/accounts/auth/logout/',
    TOKEN_REFRESH: '/accounts/auth/token/refresh/',
    VERIFY_OTP: '/accounts/verify-otp/',
    RESEND_OTP: '/accounts/resend-otp/',
    FORGOT_PASSWORD: '/accounts/forgot-password/',
    RESET_PASSWORD: '/accounts/reset-password/',
  },

  // User Profile
  PROFILE: {
    ME: '/accounts/me/',
    UPDATE: '/accounts/me/',
    ADDRESSES: '/accounts/addresses/',
    ADDRESS_DETAIL: (id: string) => `/accounts/addresses/${id}/`,
  },

  // Services
  SERVICES: {
    CATEGORIES: '/services/categories/',
    ITEMS: '/services/items/',
    ITEM_DETAIL: (id: string) => `/services/items/${id}/`,
    PRICING: '/services/pricing/',
  },

  // Orders
  ORDERS: {
    LIST: '/orders/',
    CREATE: '/orders/',
    DETAIL: (id: string) => `/orders/${id}/`,
    CANCEL: (id: string) => `/orders/${id}/cancel/`,
    TRACK: (id: string) => `/orders/${id}/track/`,
    HISTORY: '/orders/history/',
  },

  // Payments
  PAYMENTS: {
    CREATE: '/payments/payments/',
    VERIFY: (id: string) => `/payments/payments/${id}/verify/`,
    METHODS: '/payments/saved-methods/',
    WALLET: '/payments/wallets/',
    REFUNDS: '/payments/refunds/',
  },

  // Notifications
  NOTIFICATIONS: {
    LIST: '/notifications/notifications/',
    UNREAD_COUNT: '/notifications/notifications/unread_count/',
    MARK_READ: (id: string) => `/notifications/notifications/${id}/mark_read/`,
    MARK_ALL_READ: '/notifications/notifications/mark_all_read/',
    PREFERENCES: '/notifications/preferences/me/',
  },

  // Chat
  CHAT: {
    ROOMS: '/chat/rooms/',
    MESSAGES: (roomId: string) => `/chat/rooms/${roomId}/messages/`,
    SEND: (roomId: string) => `/chat/rooms/${roomId}/messages/`,
    UPLOAD: '/chat/upload/',
  },

  // Tracking
  TRACKING: {
    LOCATION: (orderId: string) => `/tracking/orders/${orderId}/location/`,
    ROUTE: (orderId: string) => `/tracking/orders/${orderId}/route/`,
    SESSION: '/tracking/sessions/',
  },

  // AI Features
  AI: {
    RECOGNIZE_GARMENT: '/ai/garments/recognize/',
    RECOMMENDATIONS: '/ai/recommendations/generate/',
    ESTIMATE_PRICE: '/ai/prices/estimate/',
  },

  // Analytics (for partner app)
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    REVENUE: '/analytics/revenue/',
    ORDERS: '/analytics/orders/',
  },

  // Mobile-specific endpoints
  MOBILE: {
    DASHBOARD: '/mobile/dashboard/',
    UPLOAD_IMAGE: '/mobile/upload-image/',
  },
};

export const WEBSOCKET_EVENTS = {
  // Connection
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  ERROR: 'error',

  // Notifications
  NOTIFICATION: 'notification',
  NOTIFICATION_READ: 'notification_read',

  // Orders
  ORDER_UPDATE: 'order_update',
  ORDER_STATUS_CHANGE: 'order_status_change',

  // Chat
  CHAT_MESSAGE: 'chat_message',
  NEW_MESSAGE: 'new_message',
  TYPING_START: 'typing_start',
  TYPING_STOP: 'typing_stop',
  MESSAGE_READ: 'message_read',

  // Tracking
  LOCATION_UPDATE: 'location_update',
  ROUTE_UPDATE: 'route_update',
  ETA_UPDATE: 'eta_update',

  // Partner
  PARTNER_STATUS: 'partner_status',
  NEW_ORDER_ASSIGNED: 'new_order_assigned',
};

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
};
