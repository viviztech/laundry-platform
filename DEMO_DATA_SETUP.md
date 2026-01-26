# LaundryConnect Demo Data Setup Guide

## Overview
This document describes the demo data that has been seeded into the LaundryConnect platform for testing and demonstration purposes.

## What Was Created

### 1. User Groups & Permissions (4 Groups)

#### Customer Group
- **Description:** Regular customers who place orders
- **Permissions:**
  - Create, view, and modify their own orders
  - Manage their addresses (add, view, change, delete)
  - View their wallet balance

#### Partner Group
- **Description:** Laundry service partners
- **Permissions:**
  - View and update their business profile
  - View and update assigned orders
  - Manage their availability schedule

#### Admin Group
- **Description:** Platform administrators with full access
- **Permissions:**
  - Full CRUD on orders, services, categories, pricing zones
  - View and manage users and partners
  - View and modify wallets

#### Support Group
- **Description:** Customer support staff
- **Permissions:**
  - View and modify orders
  - View user and partner information (read-only)

---

### 2. Pricing Zones (3 Zones)

| Zone | Name | Description | Price Multiplier |
|------|------|-------------|------------------|
| A | Zone A - Premium | Premium areas with higher pricing | 1.2x |
| B | Zone B - Standard | Standard residential areas | 1.0x |
| C | Zone C - Economy | Economy areas with competitive pricing | 0.9x |

---

### 3. Service Categories (5 Categories)

1. **Wash & Iron** - Complete washing and ironing service for all garments
2. **Dry Cleaning** - Professional dry cleaning for delicate fabrics
3. **Iron Only** - Quick ironing service for clean clothes
4. **Wash Only** - Washing service without ironing
5. **Premium Care** - Special care for premium and designer garments

---

### 4. Garment Types (11 Types)

**Wash & Iron Category:**
- Shirt
- T-Shirt
- Jeans
- Trousers
- Saree
- Kurta

**Dry Cleaning Category:**
- Suit (2-piece)
- Suit (3-piece)
- Blazer
- Dress

**Premium Care Category:**
- Wedding Attire

---

### 5. Services with Zone-based Pricing (11 Services)

Each service has pricing configured for all 3 zones (A, B, C) with both base price and discount price.

| Service | Base Price (Zone B) | Category |
|---------|---------------------|----------|
| Wash & Iron - Shirt | ₹30 | Wash & Iron |
| Wash & Iron - T-Shirt | ₹25 | Wash & Iron |
| Wash & Iron - Jeans | ₹50 | Wash & Iron |
| Wash & Iron - Trousers | ₹40 | Wash & Iron |
| Wash & Iron - Saree | ₹80 | Wash & Iron |
| Wash & Iron - Kurta | ₹45 | Wash & Iron |
| Dry Clean - Suit (2-piece) | ₹300 | Dry Cleaning |
| Dry Clean - Suit (3-piece) | ₹400 | Dry Cleaning |
| Dry Clean - Blazer | ₹200 | Dry Cleaning |
| Dry Clean - Dress | ₹150 | Dry Cleaning |
| Premium Care - Wedding Attire | ₹800 | Premium Care |

**Note:** Prices vary by zone:
- Zone A (Premium): Base price × 1.2
- Zone B (Standard): Base price × 1.0
- Zone C (Economy): Base price × 0.9

---

### 6. Demo User Accounts

#### Customers (5 Accounts)

Each customer has:
- A verified account
- User profile with preferences
- 1-2 addresses in Bangalore
- A wallet with random balance (₹0-500)
- Assigned to "Customer" group

| Email | Name | Phone | Password |
|-------|------|-------|----------|
| demo.customer@test.com | Demo Customer | +919000000001 | demo123 |
| rajesh.kumar@gmail.com | Rajesh Kumar | +919000000002 | demo123 |
| priya.sharma@gmail.com | Priya Sharma | +919000000003 | demo123 |
| amit.patel@gmail.com | Amit Patel | +919000000004 | demo123 |
| sneha.reddy@gmail.com | Sneha Reddy | +919000000005 | demo123 |

#### Partners (3 Businesses)

Each partner has:
- A verified business account
- Complete business profile
- Availability schedule (Monday-Saturday, 9 AM - 9 PM)
- Random ratings and order statistics
- Assigned to "Partner" group

| Email | Business Name | Type | Location | Zone | Password |
|-------|---------------|------|----------|------|----------|
| cleanpro@business.com | CleanPro Laundry Services | Laundry | Indiranagar | Zone A | partner123 |
| sparklewash@business.com | Sparkle Wash & Dry | Dry Cleaning | Koramangala | Zone B | partner123 |
| freshclean@business.com | Fresh & Clean Laundry | Laundry | HSR Layout | Zone C | partner123 |

#### Staff Accounts (2 Accounts)

| Email | Role | Group | Password |
|-------|------|-------|----------|
| admin@laundryconnect.com | Admin User | Admin | admin123 |
| support@laundryconnect.com | Support Agent | Support | admin123 |

---

### 7. Sample Orders (15 Orders)

Sample orders have been created with:
- Random order statuses (pending, confirmed, picked_up, in_progress, ready, delivered)
- 2-5 service items per order
- Proper pricing calculation including tax (18% GST) and delivery fees
- Created over the last 30 days
- Assigned to random customers and partners

---

## Demo Login Credentials

### 🧑 Customer Account
```
Email: demo.customer@test.com
Password: demo123
```
Use this to test the customer experience - placing orders, managing addresses, viewing wallet.

### 🏢 Partner Account
```
Email: cleanpro@business.com
Password: partner123
```
Use this to test the partner dashboard - viewing assigned orders, managing availability.

### 👨‍💼 Admin Account
```
Email: admin@laundryconnect.com
Password: admin123
```
Use this for full platform administration.

### 🎧 Support Account
```
Email: support@laundryconnect.com
Password: admin123
```
Use this to test customer support features.

---

## Mobile App Configuration

The React Native mobile app has been configured with proper package identifiers:

- **iOS Bundle Identifier:** `com.laundryconnect.mobile`
- **Android Package:** `com.laundryconnect.mobile`

The app can now be opened on Android/iOS simulators using:
```bash
cd mobile
npx expo start
# Then press 'a' for Android or 'i' for iOS
```

---

## Re-seeding Data

To re-seed the demo data, run:

```bash
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py shell < seed_demo_data.py
```

The script is idempotent and will skip creating duplicate data.

---

## Database Schema Summary

The demo data covers the following models:

- **Auth:** User, Group, Permission
- **Accounts:** UserProfile, Address
- **Services:** ServiceCategory, GarmentType, Service, PricingZone, ServicePricing
- **Partners:** Partner, PartnerAvailability
- **Orders:** Order, OrderItem
- **Payments:** Wallet

---

## Testing Scenarios

### Customer Flow
1. Login as `demo.customer@test.com`
2. Browse services by category
3. Add items to cart
4. Select pickup/delivery address
5. Place order
6. View order history
7. Check wallet balance

### Partner Flow
1. Login as `cleanpro@business.com`
2. View assigned orders
3. Update order status
4. Manage availability schedule
5. View earnings and statistics

### Admin Flow
1. Login as `admin@laundryconnect.com`
2. View all orders
3. Manage services and pricing
4. View partner performance
5. Manage user accounts

---

## Notes

- All passwords are set to simple demo passwords (`demo123`, `partner123`, `admin123`)
- Phone numbers use the format `+9190XXXXXXXX` or `+9191XXXXXXXX` to avoid conflicts
- Addresses are fictional but use real Bangalore area names
- Order dates are randomly distributed over the last 30 days
- Partner ratings are randomly generated between 4.0-5.0

**⚠️ Important:** This is demo data for development/testing only. Do not use in production.
