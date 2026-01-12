# LaundryConnect Serverless Deployment Guide
**Free Hosting for Admin Panel & API - Partner Launch Edition**

---

## 🎯 Overview

This guide shows how to deploy LaundryConnect using **100% FREE** services for your partner launch. Perfect for MVP testing with real users before scaling.

### **Free Tier Services We'll Use:**

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| **Railway** | Django API & Admin | 500 hours/month |
| **Neon** | PostgreSQL Database | 0.5 GB storage |
| **Upstash Redis** | Redis Cache & Sessions | 10K commands/day |
| **Cloudflare** | CDN & Static Files | Unlimited bandwidth |
| **GitHub Actions** | CI/CD Pipeline | 2000 minutes/month |

**Total Cost: $0/month** for launch! 🎉

---

## 🚀 Option 1: Railway (Recommended)

Railway offers the easiest deployment with generous free tier.

### **Step 1: Prepare Your App**

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements/production.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn config.wsgi:application",
    "healthcheckPath": "/api/health/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

Create `Procfile`:
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
worker: celery -A config worker --loglevel=info
beat: celery -A config beat --loglevel=info
```

Create `runtime.txt`:
```
python-3.11
```

### **Step 2: Update Requirements**

Create `requirements/production.txt`:
```txt
# Core Django
Django==5.0.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0

# Django packages (from your existing requirements)
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
drf-spectacular==0.27.0
django-unfold==0.35.0
python-decouple==3.8

# Channels & WebSocket
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0

# Celery
celery==5.3.4
redis==5.0.1

# Storage
boto3==1.34.19
django-storages==1.14.2

# Monitoring
sentry-sdk==1.39.1
```

### **Step 3: Create Production Settings**

Update `config/settings/production.py`:
```python
"""Production settings for Railway deployment."""

from .base import *
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = [
    '.railway.app',
    'laundryconnect.com',
    'www.laundryconnect.com',
]

# CSRF & CORS
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://laundryconnect.com',
]

CORS_ALLOWED_ORIGINS = [
    'https://laundryconnect.com',
    'https://www.laundryconnect.com',
]

# Database
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Redis
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sentry Error Tracking (Optional)
if config('SENTRY_DSN', default=''):
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
```

### **Step 4: Deploy to Railway**

1. **Push to GitHub:**
```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

2. **Create Railway Account:**
   - Go to https://railway.app
   - Sign up with GitHub (free)

3. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Django

4. **Add PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway auto-creates `DATABASE_URL`

5. **Add Redis:**
   - Click "New" → "Database" → "Redis"
   - Railway auto-creates `REDIS_URL`

6. **Set Environment Variables:**
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-secret-key>
ALLOWED_HOSTS=.railway.app
DEBUG=False
```

7. **Deploy:**
   - Railway automatically builds and deploys
   - Get your URL: `https://your-app.railway.app`

### **Step 5: Initial Setup Commands**

```bash
# Railway CLI (install first)
npm i -g @railway/cli
railway login

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput
```

---

## 🚀 Option 2: Render (Alternative)

Render offers similar free tier with different features.

### **Create `render.yaml`:**

```yaml
services:
  # Web Service (Django)
  - type: web
    name: laundryconnect-api
    env: python
    region: singapore
    plan: free
    branch: main
    buildCommand: "pip install -r requirements/production.txt && python manage.py collectstatic --noinput && python manage.py migrate"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: laundryconnect-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: laundryconnect-redis
          property: connectionString
    healthCheckPath: /api/health/

  # Background Worker
  - type: worker
    name: laundryconnect-worker
    env: python
    region: singapore
    plan: free
    branch: main
    buildCommand: "pip install -r requirements/production.txt"
    startCommand: "celery -A config worker --loglevel=info"
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - fromGroup: laundryconnect-env

databases:
  # PostgreSQL
  - name: laundryconnect-db
    databaseName: laundry_db
    plan: free
    region: singapore

  # Redis
  - name: laundryconnect-redis
    plan: free
    region: singapore
```

### **Deploy to Render:**

1. Push to GitHub
2. Go to https://render.com
3. Sign up with GitHub
4. Click "New" → "Blueprint"
5. Connect repository
6. Render auto-deploys from `render.yaml`

---

## 🗄️ Database: Neon PostgreSQL (Free)

Neon offers generous PostgreSQL free tier.

### **Setup Neon:**

1. **Sign Up:**
   - Go to https://neon.tech
   - Sign up (free, no credit card)

2. **Create Database:**
   - Create new project
   - Database: `laundry_db`
   - Region: Choose closest

3. **Get Connection String:**
```
postgres://user:password@ep-xxx.region.neon.tech/laundry_db?sslmode=require
```

4. **Add to Railway/Render:**
   - Set as `DATABASE_URL` environment variable

**Free Tier:**
- 0.5 GB storage
- 1 project
- Auto-suspend after 5 min inactivity (resumes on connection)

---

## 🔴 Redis: Upstash (Free)

Upstash Redis for caching and sessions.

### **Setup Upstash:**

1. **Sign Up:**
   - Go to https://upstash.com
   - Sign up (free)

2. **Create Database:**
   - Name: `laundryconnect-redis`
   - Region: Choose closest
   - Type: Regional

3. **Get Connection URL:**
```
rediss://default:password@region-12345.upstash.io:6379
```

4. **Add to Environment:**
```
REDIS_URL=rediss://default:password@region-12345.upstash.io:6379
```

**Free Tier:**
- 10K commands/day
- 256 MB storage
- Perfect for sessions & cache

---

## 📦 Static Files: Cloudflare R2 (Free Alternative to S3)

### **Option 1: WhiteNoise (Simplest - Included)**

Already configured in production settings:
```python
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Serves static files directly from Django (perfect for admin panel).

### **Option 2: Cloudflare R2 (For Media Files)**

1. **Create R2 Bucket:**
   - Go to Cloudflare dashboard
   - Storage → R2
   - Create bucket: `laundryconnect-media`

2. **Configure Django:**
```python
# settings/production.py
AWS_S3_ENDPOINT_URL = 'https://xxx.r2.cloudflarestorage.com'
AWS_ACCESS_KEY_ID = config('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'laundryconnect-media'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

**Free Tier:**
- 10 GB/month storage
- No egress fees

---

## 🔐 Environment Variables

Create `.env.production`:
```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-with-django>
DEBUG=False
ALLOWED_HOSTS=.railway.app,laundryconnect.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379

# Email (SendGrid Free Tier)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@laundryconnect.com

# Payment Gateway
RAZORPAY_KEY_ID=<your-key>
RAZORPAY_KEY_SECRET=<your-secret>

# Twilio (Optional)
TWILIO_ACCOUNT_SID=<your-sid>
TWILIO_AUTH_TOKEN=<your-token>
TWILIO_PHONE_NUMBER=<your-number>

# Sentry (Optional)
SENTRY_DSN=<your-sentry-dsn>
```

---

## 🚀 Quick Deploy Script

Create `deploy.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying LaundryConnect to Railway..."

# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link project
railway link

# Deploy
railway up

# Run migrations
railway run python manage.py migrate

# Create superuser (interactive)
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo "🌐 Your admin panel: https://your-app.railway.app/admin/"
```

Make executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📊 Free Tier Limits & Monitoring

### **Railway Free Tier:**
- ✅ 500 hours/month ($5 credit)
- ✅ 1 GB RAM
- ✅ 1 GB disk
- ✅ Unlimited bandwidth
- **Sleeps after 15 min inactivity**

### **Neon PostgreSQL:**
- ✅ 0.5 GB storage
- ✅ Auto-suspends after 5 min
- **Perfect for 100-500 orders/month**

### **Upstash Redis:**
- ✅ 10K commands/day
- ✅ 256 MB RAM
- **Enough for 100 concurrent users**

### **When to Upgrade:**
- Orders > 500/month → Upgrade Railway to $5/month
- Database > 0.5 GB → Upgrade Neon to $20/month
- Redis > 10K commands/day → Upgrade Upstash to $10/month

---

## 🔧 GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway
        run: npm i -g @railway/cli

      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

      - name: Run Migrations
        run: railway run python manage.py migrate
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 🌐 Custom Domain (Free with Cloudflare)

1. **Register Domain:**
   - Use Freenom for free domains (.tk, .ml, .ga)
   - Or buy cheap domain ($1-2/year)

2. **Add to Cloudflare:**
   - Add domain to Cloudflare (free)
   - Update nameservers

3. **Configure DNS:**
```
CNAME   @       your-app.railway.app
CNAME   www     your-app.railway.app
CNAME   api     your-app.railway.app
```

4. **Update Railway:**
   - Settings → Custom Domain
   - Add: `laundryconnect.com`

5. **Enable SSL:**
   - Cloudflare auto-enables SSL (free)

---

## 📧 Email: SendGrid (Free)

Free tier: 100 emails/day

```python
# settings/production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@laundryconnect.com'
```

---

## 🔍 Monitoring: Sentry (Free)

Free tier: 5K errors/month

1. **Sign up:** https://sentry.io
2. **Create project:** Django
3. **Add to settings:** (already in production.py)
4. **Set DSN:** `SENTRY_DSN=https://xxx@sentry.io/xxx`

---

## ✅ Deployment Checklist

### **Before Deploy:**
- [ ] Update `requirements/production.txt`
- [ ] Configure `config/settings/production.py`
- [ ] Create `Procfile` and `railway.json`
- [ ] Set up environment variables
- [ ] Test locally with production settings

### **Deploy:**
- [ ] Push to GitHub
- [ ] Create Railway/Render account
- [ ] Connect repository
- [ ] Add PostgreSQL database
- [ ] Add Redis database
- [ ] Set environment variables
- [ ] Deploy!

### **After Deploy:**
- [ ] Run migrations
- [ ] Create superuser
- [ ] Collect static files
- [ ] Seed demo data (optional)
- [ ] Test admin panel
- [ ] Test API endpoints
- [ ] Configure custom domain
- [ ] Set up monitoring

---

## 🎯 Cost Breakdown

| Service | Free Tier | Paid (when needed) |
|---------|-----------|-------------------|
| Railway | 500 hrs/month | $5/month |
| Neon DB | 0.5 GB | $20/month |
| Upstash Redis | 10K cmd/day | $10/month |
| Cloudflare | Unlimited | Free forever |
| SendGrid | 100 emails/day | $15/month |
| Domain | - | $1-10/year |
| **TOTAL** | **$0/month** | **$50/month** |

---

## 🚀 Launch Day Commands

```bash
# 1. Deploy
git push origin main

# 2. Run migrations
railway run python manage.py migrate

# 3. Create admin
railway run python manage.py createsuperuser

# 4. Load demo data (optional)
railway run python manage.py shell < seed_partner_demo_data.py

# 5. Test
curl https://your-app.railway.app/api/health/
curl https://your-app.railway.app/admin/

# 6. Monitor logs
railway logs
```

---

## 📱 Mobile App Configuration

Update mobile app API endpoint:
```typescript
// mobile/src/constants/api.ts
export const API_CONFIG = {
  BASE_URL: 'https://your-app.railway.app/api',
  SOCKET_URL: 'wss://your-app.railway.app',
};
```

---

## 🐛 Troubleshooting

### **Issue: App not starting**
```bash
# Check logs
railway logs

# Common fixes
railway run python manage.py check
railway run python manage.py migrate
```

### **Issue: Static files not loading**
```bash
# Collect static files
railway run python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings
```

### **Issue: Database connection error**
```bash
# Verify DATABASE_URL
railway variables

# Test connection
railway run python manage.py dbshell
```

---

## 🎉 Success! Your Platform is Live!

After deployment, you'll have:

- ✅ Admin Panel: `https://your-app.railway.app/admin/`
- ✅ API Docs: `https://your-app.railway.app/api/docs/`
- ✅ API: `https://your-app.railway.app/api/`
- ✅ WebSocket: `wss://your-app.railway.app/ws/`

**Total Cost: $0/month** 🎉

Ready for 100-500 partners and 1000+ customers!

---

**Last Updated:** January 12, 2026
**Recommended for:** MVP & Partner Launch
**Next Step:** Monitor usage and upgrade when needed
