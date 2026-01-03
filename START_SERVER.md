# LaundryConnect - Server Startup Guide

**Last Updated**: 2026-01-02

---

## Prerequisites Checklist

Before starting the server, ensure you have:

- [ ] Python 3.14+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] Redis 7+ installed
- [ ] Virtual environment created

---

## Step-by-Step Server Startup

### 1. Create and Activate Virtual Environment

```bash
cd /Users/ganeshthangavel/projects/laundry-platform

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements/base.txt

# This will install:
# - Django 6.0
# - Django REST Framework
# - PostgreSQL adapter
# - Redis clients
# - Celery
# - Django Channels (WebSocket support)
# - Twilio (SMS)
# - PyWebPush (Push notifications)
# - And all other dependencies
```

**Expected Installation Time**: 2-5 minutes depending on your internet connection.

### 3. Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

**Minimum Required Variables**:
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DB_NAME=laundry_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 4. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE laundry_db;

# Create user (if needed)
CREATE USER postgres WITH PASSWORD 'your-password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE laundry_db TO postgres;

# Exit psql
\q
```

### 5. Run Migrations

```bash
# Make sure virtual environment is activated
python manage.py migrate

# You should see migrations being applied for:
# - accounts
# - services
# - orders
# - partners
# - payments
# - notifications
# - Django built-in apps
```

### 6. Create Superuser

```bash
python manage.py createsuperuser

# Follow the prompts:
# - Email: admin@laundryconnect.com
# - Phone: +1234567890
# - Password: (choose a secure password)
```

### 7. Load Notification Templates

```bash
# Load the 21 default notification templates
python manage.py load_notification_templates

# You should see:
# Successfully created/updated 21 notification templates
```

### 8. Start Redis Server

**Option A - Using Homebrew (macOS)**:
```bash
# Start Redis as a service
brew services start redis

# Check if running
redis-cli ping
# Should respond: PONG
```

**Option B - Manual Start**:
```bash
# Start Redis manually
redis-server

# In another terminal, verify:
redis-cli ping
```

### 9. Start Celery Worker

**Open a new terminal window**:
```bash
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate

# Start Celery worker
celery -A config worker --loglevel=info

# You should see:
# [tasks]
#   . apps.notifications.tasks.cleanup_old_notifications
#   . apps.notifications.tasks.send_bulk_notifications
#   . apps.notifications.tasks.send_daily_summary_email
#   . apps.notifications.tasks.send_notification_email
#
# celery@hostname ready.
```

**Keep this terminal running** for async email notifications to work.

### 10. Start Django Development Server

**In the original terminal** (with venv activated):
```bash
# Start Django server
python manage.py runserver

# You should see:
# Performing system checks...
# System check identified no issues (0 silenced).
# January 02, 2026 - 12:00:00
# Django version 6.0, using settings 'config.settings.development'
# Starting ASGI/Daphne development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

**Server is now running with WebSocket support!**

---

## Verify Installation

### 1. Check Django Admin

Open your browser and go to:
```
http://127.0.0.1:8000/admin/
```

Login with the superuser credentials you created.

### 2. Check API Documentation

```
http://127.0.0.1:8000/api/docs/
```

You should see Swagger UI with all API endpoints.

### 3. Check WebSocket Token

```bash
# Get your access token first by logging in
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@laundryconnect.com", "password": "your-password"}'

# Use the access token to get WebSocket token
curl -X GET http://127.0.0.1:8000/api/realtime/token/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Test WebSocket Connection (Optional)

Install wscat:
```bash
npm install -g wscat
```

Connect to WebSocket:
```bash
wscat -c "ws://localhost:8000/ws/notifications/?token=YOUR_WS_TOKEN"
```

---

## Running Services Summary

After complete setup, you should have **3 terminal windows** running:

### Terminal 1: Django Server
```bash
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate
python manage.py runserver
```
**Status**: ✅ Running on http://127.0.0.1:8000/

### Terminal 2: Celery Worker
```bash
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate
celery -A config worker --loglevel=info
```
**Status**: ✅ Ready to process async tasks

### Terminal 3: Redis Server (Optional if using brew services)
```bash
redis-server
```
**Status**: ✅ Running on port 6379

---

## Quick Start Script

For convenience, you can use the provided startup script:

```bash
# Make it executable
chmod +x start_server.sh

# Run it
./start_server.sh
```

This script will:
1. Check if virtual environment exists
2. Activate it
3. Check Redis is running
4. Run migrations
5. Start Django server

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'django'"

**Solution**: Virtual environment not activated or dependencies not installed
```bash
source venv/bin/activate
pip install -r requirements/base.txt
```

### Issue 2: "FATAL: database 'laundry_db' does not exist"

**Solution**: Create the database
```bash
createdb laundry_db
```

### Issue 3: "Error: That port is already in use"

**Solution**: Kill the process on port 8000
```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use a different port
python manage.py runserver 8001
```

### Issue 4: "Connection refused" to Redis

**Solution**: Start Redis server
```bash
# Check if Redis is installed
redis-cli --version

# Start Redis
brew services start redis
# OR
redis-server
```

### Issue 5: Celery not processing tasks

**Solution**:
- Ensure Redis is running
- Check Celery worker is started
- Check logs for errors

### Issue 6: WebSocket connection fails

**Solution**:
- Ensure Django Channels is installed
- Check ASGI configuration
- Verify token is valid
- Check Redis is running (channel layer)

---

## Development Workflow

### Starting Work
```bash
# Terminal 1
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate
python manage.py runserver

# Terminal 2
celery -A config worker --loglevel=info
```

### Making Changes
```bash
# After model changes
python manage.py makemigrations
python manage.py migrate

# Collect static files (if needed)
python manage.py collectstatic
```

### Testing
```bash
# Run tests (when implemented)
python manage.py test

# Check for issues
python manage.py check

# Check deployment readiness
python manage.py check --deploy
```

### Stopping Services
```bash
# Stop Django server: Ctrl+C in terminal
# Stop Celery worker: Ctrl+C in terminal
# Stop Redis:
brew services stop redis
# OR just Ctrl+C if running manually
```

---

## Production Deployment Notes

For production, you'll need:

1. **ASGI Server** (instead of runserver):
   ```bash
   daphne -b 0.0.0.0 -p 8000 config.asgi:application
   # OR
   uvicorn config.asgi:application --host 0.0.0.0 --port 8000
   ```

2. **Process Manager** (Supervisor/systemd):
   - Django/Daphne service
   - Celery worker service
   - Celery beat service (for scheduled tasks)

3. **Reverse Proxy** (Nginx):
   - Serve static files
   - SSL termination
   - WebSocket proxying

4. **Environment Variables**:
   - DEBUG=False
   - Proper SECRET_KEY
   - Database credentials
   - Email settings (SendGrid)
   - Twilio credentials (for SMS)
   - VAPID keys (for push notifications)

See deployment documentation for detailed production setup.

---

## Useful Commands

### Django Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check for issues
python manage.py check

# Load notification templates
python manage.py load_notification_templates
```

### Database
```bash
# Backup database
pg_dump laundry_db > backup.sql

# Restore database
psql laundry_db < backup.sql

# Access database
psql laundry_db
```

### Redis
```bash
# Check Redis
redis-cli ping

# Monitor Redis
redis-cli monitor

# Flush all data (CAUTION!)
redis-cli FLUSHALL
```

### Celery
```bash
# Start worker
celery -A config worker -l info

# Start worker with specific queue
celery -A config worker -Q celery,email -l info

# Purge all tasks
celery -A config purge

# Inspect active tasks
celery -A config inspect active
```

---

## Next Steps

After the server is running:

1. ✅ Access admin panel and explore
2. ✅ Test API endpoints via Swagger UI
3. ✅ Try WebSocket connections
4. ✅ Create test orders and see notifications
5. ✅ Check email output in console
6. 📚 Read testing guides for detailed testing instructions

---

**For detailed testing**: See [TESTING_GUIDE.md](TESTING_GUIDE.md)
**For WebSocket integration**: See [WEBSOCKET_INTEGRATION_GUIDE.md](WEBSOCKET_INTEGRATION_GUIDE.md)
**For notifications**: See [NOTIFICATION_TESTING_GUIDE.md](NOTIFICATION_TESTING_GUIDE.md)

---

Generated with [Claude Code](https://claude.com/claude-code)
