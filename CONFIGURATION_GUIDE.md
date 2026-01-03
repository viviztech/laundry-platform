# LaundryConnect - Configuration Guide

This guide provides comprehensive documentation for all configuration settings in the LaundryConnect platform.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Django Settings](#django-settings)
3. [Database Configuration](#database-configuration)
4. [Email Configuration](#email-configuration)
5. [SMS Configuration (Twilio)](#sms-configuration-twilio)
6. [Push Notification Configuration (VAPID)](#push-notification-configuration-vapid)
7. [Payment Gateway Configuration (Razorpay)](#payment-gateway-configuration-razorpay)
8. [WebSocket Configuration (Channels)](#websocket-configuration-channels)
9. [Celery Configuration](#celery-configuration)
10. [CORS Configuration](#cors-configuration)
11. [Static Files & Media](#static-files--media)
12. [Logging Configuration](#logging-configuration)
13. [Security Settings](#security-settings)
14. [API Configuration](#api-configuration)

---

## Environment Variables

All sensitive configuration should be stored in a `.env` file in the project root. Never commit this file to version control.

### Creating the .env File

```bash
# Create .env file
cp .env.example .env

# Edit with your values
nano .env
```

### Required Environment Variables

```env
# ==========================================
# CORE DJANGO SETTINGS
# ==========================================

# Secret key for cryptographic signing (REQUIRED)
# Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY='your-secret-key-here-change-this-in-production'

# Debug mode (REQUIRED)
# Development: True
# Production: False
DEBUG=True

# Allowed hosts (REQUIRED for production)
# Comma-separated list of allowed hostnames
ALLOWED_HOSTS='localhost,127.0.0.1,yourdomain.com'

# Environment type
DJANGO_SETTINGS_MODULE='config.settings.development'

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# PostgreSQL Configuration (REQUIRED)
DB_NAME='laundry_connect'
DB_USER='postgres'
DB_PASSWORD='your-database-password'
DB_HOST='localhost'
DB_PORT='5432'

# ==========================================
# EMAIL CONFIGURATION
# ==========================================

# Email Backend
# Development: django.core.mail.backends.console.EmailBackend
# Production: django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'

# SMTP Settings (for production)
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-app-password'
DEFAULT_FROM_EMAIL='LaundryConnect <noreply@laundryconnect.com>'

# ==========================================
# SMS CONFIGURATION (TWILIO)
# ==========================================

# Twilio Credentials (Optional - for SMS notifications)
TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN='your-twilio-auth-token'
TWILIO_PHONE_NUMBER='+1234567890'

# Twilio Status Callback URL (Optional)
TWILIO_STATUS_CALLBACK_URL='https://yourdomain.com/api/v1/notifications/sms-callback/'

# ==========================================
# PUSH NOTIFICATIONS (VAPID)
# ==========================================

# Web Push VAPID Keys (Optional - for browser push notifications)
# Generate with: python manage.py generate_vapid_keys

VAPID_PRIVATE_KEY='-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----'

VAPID_PUBLIC_KEY='BGz8P1k...'

VAPID_ADMIN_EMAIL='mailto:admin@laundryconnect.com'

# ==========================================
# PAYMENT GATEWAY (RAZORPAY)
# ==========================================

# Razorpay Credentials (REQUIRED for payments)
# Get from: https://dashboard.razorpay.com/app/keys
RAZORPAY_KEY_ID='rzp_test_xxxxxxxxxxxxx'
RAZORPAY_KEY_SECRET='your-razorpay-secret-key'

# Razorpay Webhook Secret (for webhook verification)
RAZORPAY_WEBHOOK_SECRET='your-webhook-secret'

# Payment settings
RAZORPAY_CURRENCY='INR'
RAZORPAY_PAYMENT_CAPTURE='1'  # Auto-capture (1) or manual (0)

# ==========================================
# REDIS CONFIGURATION
# ==========================================

# Redis URL (for Celery and Channels)
REDIS_URL='redis://localhost:6379/0'

# Separate Redis databases for different purposes
CELERY_BROKER_URL='redis://localhost:6379/1'
CELERY_RESULT_BACKEND='redis://localhost:6379/2'
CHANNEL_LAYERS_REDIS_URL='redis://localhost:6379/3'

# ==========================================
# CELERY CONFIGURATION
# ==========================================

# Celery settings
CELERY_TASK_ALWAYS_EAGER=False  # Set True for synchronous testing
CELERY_TASK_EAGER_PROPAGATES=True

# ==========================================
# CORS SETTINGS
# ==========================================

# CORS allowed origins (for frontend apps)
CORS_ALLOWED_ORIGINS='http://localhost:3000,http://localhost:8080'

# Or allow all (development only)
CORS_ALLOW_ALL_ORIGINS=True

# ==========================================
# AWS/S3 CONFIGURATION (Optional - for media storage)
# ==========================================

# AWS credentials (if using S3 for media files)
AWS_ACCESS_KEY_ID='your-aws-access-key'
AWS_SECRET_ACCESS_KEY='your-aws-secret-key'
AWS_STORAGE_BUCKET_NAME='laundryconnect-media'
AWS_S3_REGION_NAME='us-east-1'
AWS_S3_CUSTOM_DOMAIN='your-cloudfront-domain.cloudfront.net'

# Use S3 for media files
USE_S3=False  # Set True to enable S3

# ==========================================
# SENTRY CONFIGURATION (Optional - for error tracking)
# ==========================================

# Sentry DSN (for production error tracking)
SENTRY_DSN='https://xxx@sentry.io/xxx'
SENTRY_ENVIRONMENT='production'

# ==========================================
# GOOGLE MAPS API (Optional - for location features)
# ==========================================

# Google Maps API Key
GOOGLE_MAPS_API_KEY='your-google-maps-api-key'

# ==========================================
# FRONTEND URL
# ==========================================

# Frontend application URL (for links in emails)
FRONTEND_URL='http://localhost:3000'

# ==========================================
# SECURITY SETTINGS (Production)
# ==========================================

# HTTPS/SSL settings (production only)
SECURE_SSL_REDIRECT=False  # Set True in production with HTTPS
SESSION_COOKIE_SECURE=False  # Set True in production with HTTPS
CSRF_COOKIE_SECURE=False  # Set True in production with HTTPS
SECURE_HSTS_SECONDS=0  # Set to 31536000 (1 year) in production
```

---

## Django Settings

### Settings Structure

LaundryConnect uses a split settings configuration:

```
config/settings/
├── __init__.py
├── base.py           # Common settings for all environments
├── development.py    # Development-specific settings
└── production.py     # Production-specific settings (create this)
```

### Switching Environments

```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

### Base Settings (config/settings/base.py)

Core settings shared across all environments:

```python
# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    'django_celery_beat',

    # Local apps
    'apps.accounts',
    'apps.partners',
    'apps.services',
    'apps.orders',
    'apps.payments',
    'apps.notifications',
]

# Authentication
AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## Database Configuration

### PostgreSQL Setup

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql

   # Ubuntu
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**:
   ```bash
   # Start PostgreSQL
   brew services start postgresql  # macOS
   sudo service postgresql start   # Ubuntu

   # Create database and user
   psql postgres
   ```

   ```sql
   CREATE DATABASE laundry_connect;
   CREATE USER laundry_user WITH PASSWORD 'your-password';
   ALTER ROLE laundry_user SET client_encoding TO 'utf8';
   ALTER ROLE laundry_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE laundry_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE laundry_connect TO laundry_user;
   \q
   ```

3. **Configure in .env**:
   ```env
   DB_NAME='laundry_connect'
   DB_USER='laundry_user'
   DB_PASSWORD='your-password'
   DB_HOST='localhost'
   DB_PORT='5432'
   ```

### Settings Configuration

In `config/settings/base.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}
```

### Run Migrations

```bash
python manage.py migrate
```

---

## Email Configuration

### Development (Console Backend)

In `config/settings/development.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Emails are printed to console instead of being sent.

### Production (SMTP)

In `config/settings/production.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated password

3. **Configure .env**:
   ```env
   EMAIL_HOST='smtp.gmail.com'
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER='your-email@gmail.com'
   EMAIL_HOST_PASSWORD='your-16-char-app-password'
   DEFAULT_FROM_EMAIL='LaundryConnect <noreply@yourdomain.com>'
   ```

### Testing Email

```python
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test message',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

---

## SMS Configuration (Twilio)

### Twilio Setup

1. **Create Twilio Account**: https://www.twilio.com/try-twilio

2. **Get Credentials**:
   - Account SID: Dashboard → Account Info
   - Auth Token: Dashboard → Account Info
   - Phone Number: Phone Numbers → Get a Number

3. **Configure .env**:
   ```env
   TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
   TWILIO_AUTH_TOKEN='your-auth-token'
   TWILIO_PHONE_NUMBER='+1234567890'
   TWILIO_STATUS_CALLBACK_URL='https://yourdomain.com/api/v1/notifications/sms-callback/'
   ```

### Settings Configuration

In `config/settings/development.py`:

```python
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
TWILIO_STATUS_CALLBACK_URL = config('TWILIO_STATUS_CALLBACK_URL', default='')
```

### Testing SMS

```python
from apps.notifications.sms import sms_service

result = sms_service.send_sms(
    to_number='+1234567890',
    message='Test SMS from LaundryConnect'
)

print(result)
```

### Disabling SMS (Development)

Leave SMS credentials empty in `.env` to disable SMS:

```env
TWILIO_ACCOUNT_SID=''
TWILIO_AUTH_TOKEN=''
TWILIO_PHONE_NUMBER=''
```

---

## Push Notification Configuration (VAPID)

### VAPID Key Generation

1. **Generate Keys**:
   ```bash
   python manage.py generate_vapid_keys
   ```

2. **Copy Output to .env**:
   ```env
   VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
   MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
   -----END PRIVATE KEY-----"

   VAPID_PUBLIC_KEY="BGz8P1k..."

   VAPID_ADMIN_EMAIL="mailto:admin@laundryconnect.com"
   ```

### Settings Configuration

In `config/settings/development.py`:

```python
# Web Push Notifications (VAPID)
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY', default='')
VAPID_ADMIN_EMAIL = config('VAPID_ADMIN_EMAIL',
                           default='mailto:admin@laundryconnect.com')
```

### Security Best Practices

- ✅ Keep private key secret
- ✅ Store in environment variables
- ✅ Never commit to version control
- ✅ Generate new keys for each environment
- ✅ Public key can be shared safely

### Testing Push Notifications

1. **Check Configuration**:
   ```python
   from apps.notifications.push import push_service

   if push_service.is_enabled():
       print("Push service is configured")
   else:
       print("Push service is not configured")
   ```

2. **Send Test Push** (via Django Admin):
   - Navigate to Notifications → Push Subscriptions
   - Select a subscription
   - Choose "Send test push notification" action

---

## Payment Gateway Configuration (Razorpay)

### Razorpay Setup

1. **Create Account**: https://razorpay.com/

2. **Get API Keys**:
   - Login to Dashboard
   - Settings → API Keys
   - Generate Test Keys (for development)
   - Generate Live Keys (for production)

3. **Configure .env**:
   ```env
   # Test Mode
   RAZORPAY_KEY_ID='rzp_test_xxxxxxxxxxxxx'
   RAZORPAY_KEY_SECRET='your-test-secret-key'

   # Live Mode (production)
   # RAZORPAY_KEY_ID='rzp_live_xxxxxxxxxxxxx'
   # RAZORPAY_KEY_SECRET='your-live-secret-key'

   RAZORPAY_WEBHOOK_SECRET='your-webhook-secret'
   RAZORPAY_CURRENCY='INR'
   RAZORPAY_PAYMENT_CAPTURE='1'
   ```

### Settings Configuration

In `config/settings/base.py`:

```python
# Razorpay Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')
RAZORPAY_WEBHOOK_SECRET = config('RAZORPAY_WEBHOOK_SECRET', default='')
RAZORPAY_CURRENCY = config('RAZORPAY_CURRENCY', default='INR')
RAZORPAY_PAYMENT_CAPTURE = config('RAZORPAY_PAYMENT_CAPTURE',
                                   default='1', cast=int)
```

### Webhook Configuration

1. **Configure Webhook URL** in Razorpay Dashboard:
   ```
   https://yourdomain.com/api/v1/payments/razorpay/webhook/
   ```

2. **Select Events**:
   - payment.captured
   - payment.failed
   - payment.authorized
   - refund.created
   - refund.processed

3. **Copy Webhook Secret** to .env

### Testing Payments

Use Razorpay test cards: https://razorpay.com/docs/payments/payments/test-card-details/

```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
```

---

## WebSocket Configuration (Channels)

### Redis Setup

1. **Install Redis**:
   ```bash
   # macOS
   brew install redis

   # Ubuntu
   sudo apt install redis-server
   ```

2. **Start Redis**:
   ```bash
   # macOS
   brew services start redis

   # Ubuntu
   sudo service redis-server start
   ```

3. **Verify Redis**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Settings Configuration

In `config/settings/base.py`:

```python
# Channels Configuration
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('CHANNEL_LAYERS_REDIS_URL',
                           default='redis://localhost:6379/3')],
        },
    },
}
```

### Testing WebSocket

```python
# Test channel layers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

# Send message
async_to_sync(channel_layer.group_send)(
    'test_group',
    {
        'type': 'test_message',
        'message': 'Hello WebSocket!'
    }
)
```

---

## Celery Configuration

### Celery Settings

In `config/settings/base.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL',
                           default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND',
                               default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

### Running Celery

```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat (for scheduled tasks)
celery -A config beat -l info

# Both together
celery -A config worker -l info -B
```

### Monitoring Celery

```bash
# Flower (web-based monitoring)
pip install flower
celery -A config flower
# Access at: http://localhost:5555
```

---

## CORS Configuration

### Development Settings

In `config/settings/development.py`:

```python
# CORS settings for development (allow all origins)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### Production Settings

In `config/settings/production.py`:

```python
# CORS settings for production (specific origins only)
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
    'https://app.yourdomain.com',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

---

## Static Files & Media

### Static Files

In `config/settings/base.py`:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Media Files

```python
# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

### S3 Configuration (Optional)

For production, use S3 for media files:

```python
if config('USE_S3', cast=bool, default=False):
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN')

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

---

## Logging Configuration

### Development Logging

In `config/settings/development.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Show SQL queries
            'propagate': False,
        },
    },
}
```

### Production Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/laundryconnect/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Security Settings

### Development

In `config/settings/development.py`:

```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

# Security settings (disabled for development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
```

### Production

In `config/settings/production.py`:

```python
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Security settings (HTTPS required)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Additional security headers
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
```

---

## API Configuration

### REST Framework Settings

In `config/settings/base.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}
```

---

## Quick Setup Checklist

### Development Environment

- [ ] Install Python 3.10+
- [ ] Install PostgreSQL
- [ ] Install Redis
- [ ] Create virtual environment
- [ ] Install dependencies: `pip install -r requirements/base.txt`
- [ ] Create `.env` file from template
- [ ] Configure database in `.env`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Generate VAPID keys: `python manage.py generate_vapid_keys`
- [ ] Start Redis: `redis-server`
- [ ] Start Celery: `celery -A config worker -l info`
- [ ] Start Django: `python manage.py runserver`

### Production Environment

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL with strong password
- [ ] Configure Redis with authentication
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure email SMTP
- [ ] Set up Razorpay live keys
- [ ] Configure Twilio (if using SMS)
- [ ] Set up S3 for media files (optional)
- [ ] Configure Sentry for error tracking
- [ ] Set strong `SECRET_KEY`
- [ ] Enable security settings
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set up process manager (Supervisor/systemd)
- [ ] Configure web server (Nginx/Apache)
- [ ] Set up database backups
- [ ] Configure monitoring

---

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Redis Connection Error**:
   - Verify Redis is running: `redis-cli ping`
   - Check Redis URL in `.env`

3. **Email Not Sending**:
   - Check email configuration in `.env`
   - Verify SMTP credentials
   - Check spam folder

4. **Celery Tasks Not Running**:
   - Ensure Redis is running
   - Verify Celery worker is started
   - Check Celery logs for errors

5. **Push Notifications Not Working**:
   - Verify VAPID keys are configured
   - Check browser console for errors
   - Ensure HTTPS in production

---

## Support

For configuration help:
1. Check this guide
2. Review `.env.example`
3. Check phase documentation
4. Review Django logs
5. Test each service individually

---

**Last Updated**: January 3, 2026
**Version**: 1.0
