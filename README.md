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

## Features Implemented (Phase 1)

### Authentication & User Management
- Custom User model with email-based authentication
- JWT token authentication with refresh and blacklist
- User registration and login APIs
- Password change functionality
- User profile management
- Multiple address management with geolocation support

### Admin Panel
- Complete Django admin interface
- User management
- Address management
- Token blacklist management

### API Documentation
- Interactive Swagger UI
- ReDoc documentation
- OpenAPI 3.0 schema

## Project Structure

```
laundry-platform/
├── apps/
│   └── accounts/           # User authentication and management
│       ├── migrations/
│       ├── admin.py
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── requirements/
│   ├── base.txt          # Base dependencies
│   ├── development.txt   # Development dependencies
│   └── production.txt    # Production dependencies
├── manage.py
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.14+
- PostgreSQL 15+
- Redis 7+

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

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Default Credentials

**Admin Panel Access:**
- URL: http://127.0.0.1:8000/admin/
- Email: admin@laundryconnect.com
- Password: Admin@12345

## API Endpoints

### Authentication
- `POST /api/accounts/auth/register/` - Register new user
- `POST /api/accounts/auth/login/` - User login
- `POST /api/accounts/auth/logout/` - User logout
- `POST /api/accounts/auth/token/refresh/` - Refresh JWT token

### User Management
- `GET /api/accounts/me/` - Get current user
- `PUT /api/accounts/me/` - Update current user
- `PATCH /api/accounts/me/` - Partial update current user
- `POST /api/accounts/change-password/` - Change password

### Address Management
- `GET /api/accounts/addresses/` - List user addresses
- `POST /api/accounts/addresses/` - Create new address
- `GET /api/accounts/addresses/{id}/` - Get address details
- `PUT /api/accounts/addresses/{id}/` - Update address
- `PATCH /api/accounts/addresses/{id}/` - Partial update address
- `DELETE /api/accounts/addresses/{id}/` - Delete address (soft delete)

### API Documentation
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- OpenAPI Schema: http://127.0.0.1:8000/api/schema/

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
```

## Roadmap

### Phase 2: Orders & Services (Weeks 5-8)
- Order management system
- Service catalog
- Pricing engine
- Payment integration

### Phase 3: Partner Management (Weeks 9-12)
- Partner onboarding
- Capacity management
- Assignment algorithm
- Partner dashboard

### Phase 4: Tracking & Notifications (Weeks 13-16)
- Real-time order tracking
- Push notifications
- SMS/Email notifications
- Delivery management

### Phase 5: AI & Analytics (Weeks 17-20)
- AI garment recognition
- Analytics dashboard
- Reports and insights
- Performance optimization

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
