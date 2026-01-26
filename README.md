# LaundryConnect Platform

A comprehensive web and mobile laundry aggregator platform similar to DhobiG and TumbleDry, built with Django and React.

## Project Overview

LaundryConnect is a full-stack laundry management platform that connects customers with laundry service providers. The platform includes features for order booking, dynamic pricing, real-time tracking, partner management, and AI-powered garment recognition.

## Tech Stack

### Backend
- **Framework**: Django 5.0
- **API**: Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Database**: PostgreSQL 15 with PostGIS
- **Caching**: Redis 7+
- **Task Queue**: Celery
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Python**: 3.14

### Frontend (Planned)
- **Web**: React with TypeScript
- **Mobile**: React Native
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI / Tailwind CSS

## Features Implemented

### ✅ Phase 1: Authentication & User Management
- Custom User model with email-based authentication
- JWT token authentication with refresh and blacklist
- User registration and login APIs
- Password change functionality
- User profile management
- Multiple address management with geolocation support

### ✅ Phase 2: Services & Orders
- Service catalog with categories and items
- Zone-based dynamic pricing
- Order management system
- Order status tracking
- Order assignment to partners

### ✅ Phase 3: Partner Management
- Partner registration and onboarding
- Partner verification and status management
- Service area management
- Capacity and availability tracking
- Partner performance metrics
- Holiday and availability scheduling

### ✅ Phase 4: Payment Integration
- Multiple payment gateway support (Razorpay, Stripe, PayU)
- Digital wallet system with transaction history
- Saved payment methods (cards, UPI, netbanking)
- Refund management with admin workflow
- Automatic unique ID generation for all transactions
- Comprehensive payment tracking and reporting

### ✅ Phase 5: Notifications System
- In-app notification system with 21+ notification types
- Automated email notifications for all order and payment events
- Beautiful HTML email templates with responsive design
- Asynchronous email sending via Celery
- User notification preferences and customization
- Real-time notification counts and status tracking
- Signal-based automatic notification creation
- Bulk notification system for promotions
- Email delivery tracking and retry logic

### ✅ Phase 6: Real-time WebSocket Features
- Django Channels integration with ASGI support
- Real-time notifications via WebSockets
- Live order tracking and status updates
- Partner real-time updates for order assignments
- JWT-based WebSocket authentication
- Automatic reconnection handling
- Redis channel layer for message broadcasting
- Frontend integration guide with JavaScript examples
- Browser notification support

### ✅ Phase 7 (Part 1): SMS Notifications (Just Completed!)
- Twilio SMS integration for instant notifications
- 21+ SMS templates for order and payment events
- User SMS preferences with opt-in/opt-out controls
- Multi-channel notifications (Email + SMS + WebSocket)
- Async SMS sending via Celery for performance
- Delivery tracking with message SID and status
- Phone number validation (E.164 format)
- SMS testing command for development
- Comprehensive error handling and retry logic
- Cost tracking and usage monitoring support

### Admin Panel
- Complete Django admin interface for all models
- User, partner, order, payment management
- Inline editing for related models
- Advanced filtering and search

### API Documentation
- Interactive Swagger UI
- ReDoc documentation
- OpenAPI 3.0 schema

## Project Structure

```
laundry-platform/
├── apps/
│   ├── accounts/           # User authentication and management
│   ├── services/           # Service catalog and pricing
│   ├── orders/             # Order management
│   ├── partners/           # Partner management
│   ├── payments/           # Payment and wallet system
│   └── notifications/      # Notification and email system
├── config/
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── requirements/
│   ├── base.txt           # Base dependencies
│   ├── development.txt    # Development dependencies
│   └── production.txt     # Production dependencies
├── manage.py
├── start_server.sh               # Quick start script
├── QUICK_START.md                # Quick start guide
├── TESTING_GUIDE.md              # API testing guide
├── NOTIFICATION_TESTING_GUIDE.md # Notification testing guide
├── PHASE_4_SUMMARY.md            # Payment implementation summary
├── PHASE_5_SUMMARY.md            # Notification implementation summary
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.14+
- PostgreSQL 15+
- Redis 7+ (required for Celery)
- Celery (for async task processing)

### Installation

1. **Clone the repository**
   ```bash
   cd ~/projects/laundry-platform
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb laundry_db
   ```

6. **Run migrations**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.development
   python manage.py migrate
   ```

7. **Load notification templates**
   ```bash
   python manage.py load_notification_templates
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Start Redis server** (required for WebSockets and Celery)
   ```bash
   redis-server
   # Or on Mac with Homebrew: brew services start redis
   ```

10. **Start Celery worker** (for async email and SMS notifications)
   ```bash
   # In a new terminal
   celery -A config worker --loglevel=info
   ```

11. **Run development server**
   ```bash
   # Quick method (recommended)
   ./start_server.sh

   # Or manual method
   python manage.py runserver
   ```

### Quick Start

For a faster setup, see [QUICK_START.md](QUICK_START.md)

### Default Credentials

**Admin Panel Access:**
- URL: http://127.0.0.1:8000/admin/
- Create your own superuser with: `python manage.py createsuperuser`

## API Endpoints

### 📍 Access Points
- **Swagger UI** (Interactive Testing): http://localhost:8000/api/docs/
- **ReDoc** (Documentation): http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

### Authentication & Accounts
- `POST /api/accounts/register/` - Register new user
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/token/refresh/` - Refresh JWT token
- `GET /api/accounts/profile/` - Get/update user profile
- `POST /api/accounts/addresses/` - Manage addresses

### Services
- `GET /api/services/categories/` - List service categories
- `GET /api/services/items/` - List service items
- `GET /api/services/pricing-zones/` - List pricing zones
- `GET /api/services/pricing-tiers/` - List pricing tiers

### Orders
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Order details
- `POST /api/orders/{id}/cancel/` - Cancel order
- `POST /api/orders/{id}/assign/` - Assign partner (admin)

### Partners
- `GET /api/partners/partners/` - List partners
- `POST /api/partners/partners/` - Register as partner
- `GET /api/partners/partners/available/` - Find available partners
- `POST /api/partners/partners/{id}/verify/` - Verify partner (admin)

### Payments
- `POST /api/payments/payments/` - Create payment
- `POST /api/payments/payments/{id}/verify/` - Verify payment
- `GET /api/payments/wallets/` - Get wallet balance
- `POST /api/payments/wallets/{id}/add_balance/` - Add wallet balance
- `POST /api/payments/refunds/` - Request refund
- `POST /api/payments/payment-methods/` - Add payment method

### Notifications (New!)
- `GET /api/notifications/` - List user notifications
- `GET /api/notifications/unread_count/` - Get unread count
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `GET /api/notifications/preferences/me/` - Get preferences
- `PUT /api/notifications/preferences/me/` - Update preferences
- `POST /api/notifications/bulk/` - Send bulk notifications (admin)

**For complete API reference, visit the Swagger UI at `/api/docs/`**

## Database Models

### User
- UUID primary key
- Email and phone (unique)
- User type: customer, partner, admin
- Status flags: is_active, is_staff, is_verified
- Timestamps: date_joined, updated_at, last_login

### UserProfile
- One-to-one with User
- Profile image
- Personal information (DOB, gender)
- Preferences (language, notifications)

### Address
- Multiple addresses per user
- Geolocation support (latitude, longitude)
- Zone-based pricing support
- Contact information
- Default address flag
- Soft delete support

## Development

### Running Tests
```bash
python manage.py test
```

### Verification Script
```bash
python verify_setup.py
```

This script verifies:
- Database connection
- Superuser creation
- Password hashing
- JWT token generation
- User and profile creation
- Address management
- URL configuration
- Settings validation

### Code Quality
```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy .
```

## Environment Variables

Required environment variables (see `.env.example`):

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=laundry_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Email (Development - Console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Email (Production - SendGrid)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-sendgrid-username
# EMAIL_HOST_PASSWORD=your-sendgrid-password
# DEFAULT_FROM_EMAIL=noreply@laundryconnect.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Twilio SMS (Phase 7)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+919876543210
```

## Roadmap

### ✅ Phase 1: Foundation (Weeks 1-4) - COMPLETED
- User authentication and management
- Custom user model with profiles
- Address management

### ✅ Phase 2: Services & Orders (Weeks 5-8) - COMPLETED
- Service catalog and categories
- Zone-based pricing
- Order management system

### ✅ Phase 3: Partner Management (Weeks 9-12) - COMPLETED
- Partner onboarding and verification
- Service area management
- Capacity tracking

### ✅ Phase 4: Payment Integration (Week 13) - COMPLETED
- Multi-gateway payment support
- Digital wallet system
- Refund management
- Saved payment methods

### ✅ Phase 5: Notifications (Week 14) - COMPLETED
- In-app notification system
- Email notifications with 21+ templates
- Asynchronous email sending
- User notification preferences
- Signal-based auto-notifications
- Bulk notification system

### ✅ Phase 6: Real-time Features (Week 15) - COMPLETED
- WebSocket support with Django Channels
- Real-time order tracking
- Live notifications
- JWT-authenticated WebSocket connections
- Redis channel layer for broadcasting

### 🔄 Phase 7: Enhanced Real-time Features (Weeks 16-17) - IN PROGRESS
- ✅ **Part 1 - SMS Notifications**: Twilio integration, 21+ templates, user preferences
- 🔜 **Part 2 - Push Notifications**: Web Push API, service workers, VAPID
- 🔜 **Part 3 - Live Chat**: Customer-partner messaging, file sharing
- 🔜 **Part 4 - Location Tracking**: Real-time GPS tracking on map

### 📋 Phase 8-20: Advanced Features (Weeks 18-20)
- Analytics dashboard
- AI garment recognition
- Performance optimization
- Mobile app development
- Advanced reporting

## Contributing

This is a private project. For development team members:

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

Proprietary - All rights reserved

## Contact

For questions or support, contact the development team.

---

Generated with [Claude Code](https://claude.com/claude-code)
