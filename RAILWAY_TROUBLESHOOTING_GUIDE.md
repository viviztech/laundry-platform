# Railway Deployment Troubleshooting & Step-by-Step Guide

**Last Updated**: January 11, 2026
**Issue**: Deployment failures on Railway
**Status**: Comprehensive troubleshooting guide

---

## 🔍 Common Railway Deployment Failures & Solutions

### Issue 1: Build Command Fails (Most Common)

**Error Messages**:
- `collectstatic: command not found`
- `No module named 'django'`
- `ImportError: cannot import name 'config'`

**Root Cause**: The build command in `railway.json` runs before environment variables are available.

**Solution**: Update railway.json to simplify build command

---

## ✅ STEP-BY-STEP: Fix Railway Deployment

### Step 1: Update railway.json (CRITICAL FIX)

Replace your `railway.json` with this simplified version:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT config.asgi:application",
    "healthcheckPath": "/admin/login/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Key Changes**:
- ✅ Removed `buildCommand` (causes issues)
- ✅ Moved `migrate` and `collectstatic` to `startCommand`
- ✅ Railway's NIXPACKS will auto-install requirements

### Step 2: Verify Dependencies in requirements/base.txt

Ensure these are present:

```txt
Django>=6.0
djangorestframework>=3.16.0
daphne>=4.0.0
channels[daphne]==4.0.0
psycopg2-binary>=2.9.9
dj-database-url==2.1.0
python-decouple==3.8
redis==5.0.1
celery==5.3.4
whitenoise>=6.6.0
gunicorn>=21.2.0
django-unfold>=0.75.0
```

### Step 3: Create nixpacks.toml (Alternative Approach)

Create this file in your project root:

```toml
# nixpacks.toml
[phases.setup]
nixPkgs = ["python312", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements/base.txt"]

[phases.build]
cmds = []

[start]
cmd = "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT config.asgi:application"
```

---

## 🚀 Complete Step-by-Step Railway Deployment

### STEP 1: Setup Railway Project (5 minutes)

#### 1.1 Create New Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Click **"Empty Project"** (we'll connect GitHub manually)
4. Name it: `laundry-platform` or `laundryconnect`

#### 1.2 Add PostgreSQL Database

1. Click **"+ New"** button
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait 30 seconds for provisioning
5. **Important**: Note that Railway automatically sets `DATABASE_URL`

#### 1.3 Add Redis Database

1. Click **"+ New"** button
2. Select **"Database"**
3. Choose **"Redis"**
4. Wait 30 seconds for provisioning
5. **Important**: Note that Railway automatically sets `REDIS_URL`

---

### STEP 2: Deploy Web Service (10 minutes)

#### 2.1 Add GitHub Repository

1. Click **"+ New"** button
2. Select **"GitHub Repo"**
3. If not connected:
   - Click **"Configure GitHub App"**
   - Authorize Railway
   - Select `viviztech/laundry-platform` repository
4. Select repository: `viviztech/laundry-platform`
5. Click **"Deploy Now"**

Railway will start building...

#### 2.2 Configure Service Settings

1. Click on your **web service** (auto-created)
2. Go to **"Settings"** tab
3. Update these settings:

**Service Name**: `web` (or `django-web`)

**Root Directory**: `/` (leave as root)

**Watch Paths**: (leave default)

---

### STEP 3: Configure Environment Variables (CRITICAL)

#### 3.1 Access Variables Editor

1. Click your **web service**
2. Go to **"Variables"** tab
3. Click **"RAW Editor"** (top right)

#### 3.2 Add Essential Variables

Copy and paste these (update values marked with `YOUR-`):

```bash
# Django Core
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-minimum-50-characters-use-strong-random-string
DEBUG=False

# Important: Update this after Railway assigns your domain
ALLOWED_HOSTS=*.railway.app

# Database (Auto-set by Railway - verify it exists)
# DATABASE_URL should already be set - don't add if exists

# Redis (Auto-set by Railway - verify it exists)
# REDIS_URL should already be set - don't add if exists

# CORS (Update with your actual domains)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Email - SendGrid (REQUIRED for notifications)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR-SENDGRID-API-KEY

# SMS - Twilio (REQUIRED for SMS notifications)
TWILIO_ACCOUNT_SID=YOUR-TWILIO-ACCOUNT-SID
TWILIO_AUTH_TOKEN=YOUR-TWILIO-AUTH-TOKEN
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications - VAPID (Generate these)
VAPID_PRIVATE_KEY=YOUR-VAPID-PRIVATE-KEY
VAPID_PUBLIC_KEY=YOUR-VAPID-PUBLIC-KEY
VAPID_ADMIN_EMAIL=mailto:admin@laundryconnect.com

# Payment Gateway - Razorpay
RAZORPAY_KEY_ID=YOUR-RAZORPAY-KEY-ID
RAZORPAY_KEY_SECRET=YOUR-RAZORPAY-SECRET

# Railway Specific
RAILWAY_ENVIRONMENT=production
```

#### 3.3 Verify Auto-Set Variables

Check that these are already set (Railway adds them automatically):

- ✅ `DATABASE_URL` - Should look like: `postgresql://...`
- ✅ `REDIS_URL` - Should look like: `redis://...`
- ✅ `PORT` - Railway sets this automatically
- ✅ `RAILWAY_ENVIRONMENT_ID` - Auto-set

**If missing**: Go to your PostgreSQL service, copy the connection string

#### 3.4 Save and Redeploy

1. Click **"Save"** or **"Deploy"**
2. Railway will restart with new environment variables

---

### STEP 4: Monitor Deployment (5 minutes)

#### 4.1 Watch Build Logs

1. Click **"Deployments"** tab
2. Click the latest deployment
3. Watch the logs:

**Successful Build Looks Like**:
```
✓ Detected Python 3.12
✓ Installing dependencies from requirements/base.txt
✓ Dependencies installed successfully
✓ Starting deployment...
✓ Running migrations...
✓ Collecting static files...
✓ Starting Daphne server...
✓ Server listening on 0.0.0.0:$PORT
```

**If Build Fails**: See [Common Errors](#common-errors-and-solutions) below

#### 4.2 Check Service Status

1. Go back to **"Overview"**
2. Your web service should show:
   - 🟢 **Active** (green dot)
   - URL: `https://your-app.railway.app`

---

### STEP 5: Run Initial Setup Commands (5 minutes)

#### 5.1 Access Railway Shell

**Option A: Railway CLI** (Recommended)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Load notification templates (optional)
railway run python manage.py load_notification_templates
```

**Option B: Railway Dashboard**

1. Click your **web service**
2. Click **"..."** menu (top right)
3. Select **"Run Command"**
4. Enter command and press Enter:

```bash
python manage.py migrate
```

Repeat for:
```bash
python manage.py createsuperuser
```

#### 5.2 Generate VAPID Keys (if not done)

```bash
railway run python manage.py generate_vapid_keys
```

Copy the output and add to Railway variables.

---

### STEP 6: Access Your Application

#### 6.1 Get Your Railway URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Copy the Railway-provided domain:
   - Example: `laundryconnect-production.up.railway.app`

#### 6.2 Update ALLOWED_HOSTS

1. Go to **"Variables"** tab
2. Update `ALLOWED_HOSTS`:
   ```
   ALLOWED_HOSTS=laundryconnect-production.up.railway.app,*.railway.app
   ```
3. Click **"Deploy"** to restart

#### 6.3 Access Admin Panel

1. Open browser: `https://your-app.up.railway.app/admin/`
2. Login with superuser credentials
3. ✅ You should see the Django Unfold admin!

---

## 🐛 Common Errors and Solutions

### Error 1: "Application failed to respond"

**Symptoms**:
- Build succeeds but app doesn't start
- Health check fails
- 503 errors

**Solutions**:

**A. Check PORT binding**:
Ensure Daphne uses Railway's PORT:
```bash
daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

**B. Verify ALLOWED_HOSTS**:
```python
ALLOWED_HOSTS=*.railway.app
```

**C. Check logs for errors**:
- Railway Dashboard → Deployments → View Logs
- Look for Python tracebacks

### Error 2: "collectstatic: command not found"

**Symptoms**:
- Build fails during collectstatic
- Cannot find manage.py

**Solutions**:

**Remove buildCommand from railway.json**:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT config.asgi:application"
  }
}
```

### Error 3: "DATABASES improperly configured"

**Symptoms**:
- Django can't connect to database
- No ENGINE value error

**Solutions**:

**A. Verify DATABASE_URL exists**:
1. Railway Dashboard → PostgreSQL service
2. Click **"Connect"** tab
3. Copy **"DATABASE_URL"**
4. Paste in web service variables

**B. Check production.py has dj_database_url**:
```python
DATABASES['default'] = dj_database_url.config(
    default=config('DATABASE_URL', default=''),
    conn_max_age=600,
)
```

### Error 4: "No module named 'decouple'"

**Symptoms**:
- Import errors during startup
- Missing python packages

**Solutions**:

**A. Verify requirements/base.txt**:
```bash
python-decouple==3.8
```

**B. Force rebuild**:
Railway Dashboard → Settings → "Trigger Deploy"

### Error 5: "500 Internal Server Error"

**Symptoms**:
- App starts but pages show 500
- Admin panel not loading

**Solutions**:

**A. Check DEBUG setting**:
```bash
DEBUG=False  # Correct for production
```

**B. Check logs**:
```bash
railway logs
```

**C. Verify SECRET_KEY**:
Must be set and at least 50 characters:
```bash
SECRET_KEY=your-super-secret-key-minimum-50-characters
```

### Error 6: Static files not loading (CSS/JS missing)

**Symptoms**:
- Admin panel loads but no styling
- 404 errors for /static/ files

**Solutions**:

**A. Verify WhiteNoise in settings**:
```python
# production.py
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**B. Run collectstatic**:
```bash
railway run python manage.py collectstatic --noinput
```

**C. Check requirements**:
```bash
whitenoise>=6.6.0
```

### Error 7: "Redis connection failed"

**Symptoms**:
- Celery worker can't connect
- Channel layers not working
- WebSocket failures

**Solutions**:

**A. Verify REDIS_URL**:
Railway Dashboard → Redis service → Connect → Copy URL

**B. Check production.py**:
```python
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
```

---

## 📊 Verify Successful Deployment

### Checklist

- [ ] Build completes without errors
- [ ] Service shows 🟢 Active status
- [ ] Railway URL accessible
- [ ] Admin panel loads at `/admin/`
- [ ] Admin panel has styling (Django Unfold)
- [ ] Can login with superuser
- [ ] No errors in deployment logs
- [ ] Database connected (DATABASE_URL set)
- [ ] Redis connected (REDIS_URL set)

### Test Endpoints

```bash
# Health check
curl https://your-app.railway.app/admin/login/
# Should return 200 OK

# API test
curl https://your-app.railway.app/api/
# Should return JSON response
```

---

## 🔄 Optional: Setup Celery Worker

### Create Worker Service

1. Railway Dashboard → **"+ New"**
2. Select **"GitHub Repo"**
3. Choose same repository: `laundry-platform`
4. After deployment, click service
5. Go to **"Settings"**
6. Under **"Deploy"** section:
   - **Start Command**:
   ```bash
   celery -A config worker --loglevel=info --concurrency=2
   ```
7. Go to **"Variables"** tab
8. Click **"Copy from another service"**
9. Select your **web service**
10. Click **"Deploy"**

### Verify Worker

Check logs:
```
[INFO] celery@worker ready.
[INFO] Connected to redis://...
```

---

## 🎯 Quick Fixes Summary

### If Build Fails:
1. ✅ Simplify railway.json (remove buildCommand)
2. ✅ Check requirements/base.txt syntax
3. ✅ Verify Python 3.12 in runtime.txt

### If App Doesn't Start:
1. ✅ Check PORT binding in start command
2. ✅ Verify ALLOWED_HOSTS includes Railway domain
3. ✅ Check logs for Python errors

### If Database Errors:
1. ✅ Verify DATABASE_URL is set
2. ✅ Run migrations: `railway run python manage.py migrate`
3. ✅ Check PostgreSQL service is running

### If Static Files Missing:
1. ✅ Verify whitenoise in requirements
2. ✅ Run collectstatic in start command
3. ✅ Check STATICFILES_STORAGE setting

---

## 🆘 Need More Help?

### Railway Resources
- **Railway Discord**: https://discord.gg/railway (fastest support)
- **Railway Docs**: https://docs.railway.app
- **Railway Status**: https://status.railway.app

### Check Logs
```bash
# Using Railway CLI
railway logs

# Or in dashboard
Railway → Your Service → View Logs
```

### Share Error Details
When asking for help, include:
1. Full error message from logs
2. railway.json content
3. Environment variables (redact secrets!)
4. Build/Deploy logs

---

## 📝 Expected Timeline

**Total Time**: 20-30 minutes

- Setup Railway project: 5 min
- Configure environment variables: 5 min
- First deployment: 5-10 min
- Run migrations: 2-3 min
- Testing: 5 min

---

**Created**: January 11, 2026
**Status**: Comprehensive troubleshooting guide

---

Generated with [Claude Code](https://claude.com/claude-code)
