/**
 * TypeScript Type Definitions
 * LaundryConnect Mobile App
 */

// User Types
export interface User {
  id: string;
  email: string;
  phone_number: string;
  full_name: string;
  role: 'customer' | 'partner' | 'admin';
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  user: User;
  profile_picture: string | null;
  date_of_birth: string | null;
  gender: 'M' | 'F' | 'O' | null;
  notification_preferences: NotificationPreferences;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  order_updates: boolean;
  promotional: boolean;
}

// Address Types
export interface Address {
  id: string;
  label: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  is_default: boolean;
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  phone_number: string;
  full_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// Service Types
export interface ServiceCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  is_active: boolean;
  display_order: number;
}

export interface ServiceItem {
  id: string;
  category: string;
  name: string;
  description: string;
  base_price: number;
  unit: string;
  image: string | null;
  is_active: boolean;
  processing_time: number;
}

export interface PricingZone {
  id: string;
  name: string;
  multiplier: number;
}

// Order Types
export type OrderStatus =
  | 'pending'
  | 'confirmed'
  | 'picked_up'
  | 'in_progress'
  | 'ready'
  | 'out_for_delivery'
  | 'delivered'
  | 'cancelled';

export interface OrderItem {
  id: string;
  service_item: ServiceItem;
  quantity: number;
  unit_price: number;
  total_price: number;
  special_instructions?: string;
}

export interface Order {
  id: string;
  order_number: string;
  user: string;
  status: OrderStatus;
  items: OrderItem[];
  pickup_address: Address;
  delivery_address: Address;
  pickup_date: string;
  delivery_date?: string;
  subtotal: number;
  tax: number;
  delivery_fee: number;
  discount: number;
  total: number;
  special_instructions?: string;
  assigned_partner?: Partner;
  created_at: string;
  updated_at: string;
}

// Partner Types
export interface Partner {
  id: string;
  business_name: string;
  contact_person: string;
  email: string;
  phone_number: string;
  rating: number;
  total_orders: number;
  is_verified: boolean;
  is_available: boolean;
}

// Payment Types
export type PaymentMethod = 'razorpay' | 'stripe' | 'payu' | 'wallet';
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';

export interface Payment {
  id: string;
  payment_id: string;
  order: string;
  amount: number;
  method: PaymentMethod;
  status: PaymentStatus;
  gateway_payment_id?: string;
  created_at: string;
}

export interface Wallet {
  id: string;
  user: string;
  balance: number;
  currency: string;
}

export interface SavedPaymentMethod {
  id: string;
  user: string;
  method_type: PaymentMethod;
  last_four: string;
  card_brand?: string;
  is_default: boolean;
}

// Notification Types
export type NotificationType =
  | 'order_created'
  | 'order_confirmed'
  | 'order_picked_up'
  | 'order_in_progress'
  | 'order_ready'
  | 'order_out_for_delivery'
  | 'order_delivered'
  | 'order_cancelled'
  | 'payment_success'
  | 'payment_failed'
  | 'general';

export interface Notification {
  id: string;
  user: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  data?: Record<string, any>;
  created_at: string;
}

// Chat Types
export interface ChatRoom {
  id: string;
  order: string;
  customer: User;
  partner?: Partner;
  created_at: string;
  last_message?: ChatMessage;
  unread_count: number;
}

export interface ChatMessage {
  id: string;
  room: string;
  sender: User;
  message: string;
  file_url?: string;
  file_type?: 'image' | 'document';
  is_read: boolean;
  created_at: string;
}

// Tracking Types
export interface LocationUpdate {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: string;
}

export interface Route {
  id: string;
  order: string;
  origin: LocationUpdate;
  destination: LocationUpdate;
  waypoints: LocationUpdate[];
  distance: number;
  duration: number;
  polyline?: string;
}

export interface TrackingSession {
  id: string;
  order: string;
  partner: string;
  start_time: string;
  end_time?: string;
  current_location?: LocationUpdate;
  route?: Route;
  eta?: string;
  status: 'active' | 'paused' | 'completed';
}

// AI Types
export interface GarmentRecognition {
  garment_type: string;
  fabric_type: string;
  color: string;
  has_stains: boolean;
  has_damage: boolean;
  estimated_price: number;
  confidence: number;
}

export interface Recommendation {
  id: string;
  type: 'service' | 'addon' | 'offer';
  item_id: string;
  title: string;
  description: string;
  confidence: number;
  reason: string;
}

// API Response Types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Navigation Types
export type RootStackParamList = {
  Splash: undefined;
  Onboarding: undefined;
  Login: undefined;
  Register: undefined;
  OTPVerification: { phone: string; email: string };
  MainTabs: undefined;
  ServiceDetails: { serviceId: string };
  OrderDetails: { orderId: string };
  Checkout: { cartItems: OrderItem[] };
  Chat: { roomId: string; orderId: string };
  Tracking: { orderId: string };
  Profile: undefined;
  Addresses: undefined;
  AddEditAddress: { addressId?: string };
  PaymentMethods: undefined;
  Settings: undefined;
};

export type TabParamList = {
  Home: undefined;
  Services: undefined;
  Orders: undefined;
  Wallet: undefined;
  Profile: undefined;
};

// Form Types
export interface LoginFormValues {
  email_or_phone: string;
  password: string;
  remember_me: boolean;
}

export interface RegisterFormValues {
  email: string;
  phone_number: string;
  full_name: string;
  password: string;
  password_confirm: string;
  agree_terms: boolean;
}

export interface AddressFormValues {
  label: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

// Redux State Types
export interface RootState {
  auth: AuthState;
  services: ServicesState;
  orders: OrdersState;
  notifications: NotificationsState;
  chat: ChatState;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface ServicesState {
  categories: ServiceCategory[];
  items: ServiceItem[];
  selectedCategory: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface OrdersState {
  orders: Order[];
  activeOrders: Order[];
  selectedOrder: Order | null;
  isLoading: boolean;
  error: string | null;
}

export interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}

export interface ChatState {
  rooms: ChatRoom[];
  messages: Record<string, ChatMessage[]>;
  activeRoom: string | null;
  isLoading: boolean;
  error: string | null;
}
