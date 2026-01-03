# Configuration Quick Start Guide

This is a quick reference guide for setting up LaundryConnect configurations.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Git

## 1. Initial Setup (5 minutes)

### Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd laundry-platform

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt
```

### Create Environment File

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

## 2. Database Setup (3 minutes)

### Install PostgreSQL

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

### Create Database

```bash
# Access PostgreSQL
psql postgres

# Run these commands:
```

```sql
CREATE DATABASE laundry_db;
CREATE USER laundry_user WITH PASSWORD 'your-password';
ALTER ROLE laundry_user SET client_encoding TO 'utf8';
ALTER ROLE laundry_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE laundry_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE laundry_db TO laundry_user;
\q
```

### Update .env

```env
DB_NAME=laundry_db
DB_USER=laundry_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## 3. Redis Setup (2 minutes)

### Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo service redis-server start
```

### Verify Redis

```bash
redis-cli ping
# Should return: PONG
```

## 4. Django Configuration (5 minutes)

### Generate Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output to `.env`:

```env
SECRET_KEY=<paste-generated-key-here>
```

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## 5. Optional Features

### A. Email Configuration (for production)

Update `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=LaundryConnect <noreply@laundryconnect.com>
```

For Gmail:
1. Enable 2FA on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password in .env

### B. SMS Notifications (Twilio)

1. Sign up at https://www.twilio.com/try-twilio
2. Get your credentials from the dashboard
3. Update `.env`:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### C. Push Notifications (VAPID)

1. Generate VAPID keys:

```bash
python manage.py generate_vapid_keys
```

2. Copy the output to `.env`:

```env
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----"
VAPID_PUBLIC_KEY="BGz8P1k..."
VAPID_ADMIN_EMAIL="mailto:admin@laundryconnect.com"
```

### D. Payment Gateway (Razorpay)

1. Sign up at https://razorpay.com/
2. Get API keys from Settings → API Keys
3. Update `.env`:

```env
# Test keys (for development)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-test-secret

# Live keys (for production)
# RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
# RAZORPAY_KEY_SECRET=your-live-secret
```

## 6. Start Services (2 minutes)

### Terminal 1: Django Server

```bash
python manage.py runserver
```

Access at: http://localhost:8000
Admin panel: http://localhost:8000/admin

### Terminal 2: Celery Worker

```bash
celery -A config worker -l info
```

### Terminal 3: Celery Beat (optional, for scheduled tasks)

```bash
celery -A config beat -l info
```

## Verification Checklist

After setup, verify everything works:

- [ ] Django server starts without errors
- [ ] Can access admin panel at /admin
- [ ] Can login with superuser credentials
- [ ] Redis is running (check Celery worker output)
- [ ] Database connection works (no migration errors)
- [ ] Static files are served correctly

### Test Commands

```bash
# Test database connection
python manage.py dbshell
\q

# Test Redis connection
redis-cli ping

# Test Celery
python manage.py shell
from apps.notifications.tasks import send_notification_email
# Should not raise errors

# Check installed apps
python manage.py check
```

## Common Issues

### Issue: Database connection error

**Solution**: Verify PostgreSQL is running and credentials in .env are correct

```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo service postgresql status  # Linux

# Test connection
psql -U laundry_user -d laundry_db -h localhost
```

### Issue: Redis connection error

**Solution**: Ensure Redis is running

```bash
# Check if Redis is running
brew services list  # macOS
sudo service redis-server status  # Linux

# Test connection
redis-cli ping
```

### Issue: SECRET_KEY missing

**Solution**: Generate and add to .env

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Issue: Celery not starting

**Solution**: Ensure Redis is running and CELERY_BROKER_URL is correct in .env

```bash
# Check Redis
redis-cli ping

# Verify .env has:
CELERY_BROKER_URL=redis://localhost:6379/1
```

### Issue: Static files not loading

**Solution**: Collect static files

```bash
python manage.py collectstatic --noinput
```

## Development vs Production

### Development Settings

```env
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CORS_ALLOW_ALL_ORIGINS=True
```

### Production Settings

```env
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Minimal Configuration (Just to Run)

If you just want to get the server running without optional features:

```env
# Minimal .env file
SECRET_KEY=<generate-with-command-above>
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DB_NAME=laundry_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Payment (use test mode)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# Leave these empty to disable
TWILIO_ACCOUNT_SID=
VAPID_PUBLIC_KEY=
```

## Next Steps

1. ✅ Complete this quick start
2. 📖 Read [CONFIGURATION_GUIDE.md](../CONFIGURATION_GUIDE.md) for detailed settings
3. 📚 Review phase documentation for feature specifics
4. 🚀 Start building!

## Getting Help

- Configuration issues? Check [CONFIGURATION_GUIDE.md](../CONFIGURATION_GUIDE.md)
- Feature questions? Check phase summary documents
- Database issues? See PostgreSQL logs: `tail -f /usr/local/var/log/postgresql@14.log`
- Redis issues? See Redis logs: `redis-cli monitor`

## Quick Reference Commands

```bash
# Start everything
python manage.py runserver          # Terminal 1
celery -A config worker -l info     # Terminal 2

# Database
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py dbshell            # Database shell

# User management
python manage.py createsuperuser    # Create admin
python manage.py changepassword     # Change password

# Testing
python manage.py test               # Run tests
python manage.py check              # Check for issues

# Utilities
python manage.py shell              # Django shell
python manage.py collectstatic      # Collect static files
python manage.py generate_vapid_keys  # Generate VAPID keys
```

---

**Time to complete**: ~15-20 minutes
**Difficulty**: Beginner-friendly
**Last updated**: January 3, 2026
