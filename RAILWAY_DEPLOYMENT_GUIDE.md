# Railway Deployment Guide - LaundryConnect Platform

**Last Updated**: January 11, 2026
**Platform**: Railway.app
**Django Version**: 6.0
**Python Version**: 3.12

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Railway Project Setup](#railway-project-setup)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Redis Setup](#redis-setup)
7. [Deployment Steps](#deployment-steps)
8. [Post-Deployment](#post-deployment)
9. [Celery Worker Setup](#celery-worker-setup)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide covers deploying the LaundryConnect platform to Railway.app, including:
- **Web Service**: Django ASGI app with WebSocket support (Daphne)
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Background Workers**: Celery worker and beat scheduler
- **Static Files**: WhiteNoise for serving static assets

---

## ✅ Prerequisites

### Local Setup
- [x] Git repository initialized
- [x] Code pushed to GitHub/GitLab/Bitbucket
- [x] Python 3.12 specified in `runtime.txt`
- [x] All dependencies in `requirements/base.txt`
- [x] Django Unfold admin UI installed
- [x] Production settings configured

### Railway Account
- [ ] Sign up at https://railway.app
- [ ] Connect your GitHub/GitLab account
- [ ] Have a credit card ready (Railway offers $5/month free tier)

---

## 🚀 Railway Project Setup

### Step 1: Create New Project

1. **Login to Railway**: https://railway.app
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `laundry-platform`
5. **Select branch**: `main` or your production branch

Railway will automatically:
- Detect Django application
- Read `railway.json` configuration
- Use `Procfile` for process definitions
- Install dependencies from `requirements/base.txt`

### Step 2: Add Services

Your project needs these services:

1. **PostgreSQL Database**
   - Click "+ New Service"
   - Select "Database"
   - Choose "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

2. **Redis**
   - Click "+ New Service"
   - Select "Database"
   - Choose "Redis"
   - Railway will automatically set `REDIS_URL`

3. **Web Service** (Auto-created)
   - Main Django application
   - Runs: `daphne -b 0.0.0.0 -p $PORT config.asgi:application`

4. **Celery Worker** (Manual setup)
   - Click "+ New Service"
   - Select "Empty Service"
   - Link to same repo
   - Configure command: `celery -A config worker --loglevel=info`

5. **Celery Beat** (Optional - for scheduled tasks)
   - Click "+ New Service"
   - Select "Empty Service"
   - Link to same repo
   - Configure command: `celery -A config beat --loglevel=info`

---

## 🔐 Environment Variables

### Required Variables

Configure these in Railway Dashboard → Your Service → Variables:

#### Django Core
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-min-50-chars-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,*.railway.app
```

#### Database (Auto-configured by Railway)
```bash
DATABASE_URL=postgresql://...  # Set automatically by Railway
```

#### Redis (Auto-configured by Railway)
```bash
REDIS_URL=redis://...  # Set automatically by Railway
```

#### CORS Settings
```bash
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-app.railway.app
```

#### Email Configuration (SendGrid)
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@laundryconnect.com
```

#### SMS (Twilio)
```bash
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

#### Push Notifications (VAPID)
```bash
VAPID_PRIVATE_KEY=your-private-key
VAPID_PUBLIC_KEY=your-public-key
VAPID_ADMIN_EMAIL=mailto:admin@laundryconnect.com
```

#### Payment Gateways
```bash
# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Stripe (if using)
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

#### Optional - Sentry (Error Tracking)
```bash
SENTRY_DSN=https://...@sentry.io/...
```

#### Railway Specific
```bash
RAILWAY_ENVIRONMENT=production
PORT=8000  # Set automatically by Railway
```

### How to Set Environment Variables

1. **Railway Dashboard** → Select your service
2. **Click "Variables" tab**
3. **Click "Raw Editor"** or add one by one
4. **Paste all variables** (one per line: `KEY=value`)
5. **Click "Deploy"** to restart with new variables

---

## 🗄️ Database Setup

### Automatic Setup (Recommended)

Railway automatically:
- Creates PostgreSQL database
- Sets `DATABASE_URL` environment variable
- Configures connection pooling

### Run Migrations

After first deployment:

```bash
# Using Railway CLI
railway run python manage.py migrate

# OR via Railway Dashboard
# Go to service → click "..." → "Run Command"
python manage.py migrate
```

### Create Superuser

```bash
# Using Railway CLI
railway run python manage.py createsuperuser

# Follow prompts to create admin user
```

### Load Initial Data (Optional)

```bash
# Load notification templates
railway run python manage.py load_notification_templates

# Seed demo data (if needed)
railway run python manage.py seed_data
```

---

## 🔴 Redis Setup

### Automatic Setup

Railway automatically:
- Creates Redis instance
- Sets `REDIS_URL` environment variable
- Configures for Celery and Channels

### Verify Redis Connection

```bash
railway run python manage.py shell

# In shell:
>>> from django.core.cache import cache
>>> cache.set('test', 'hello')
>>> cache.get('test')
'hello'
>>> exit()
```

---

## 📦 Deployment Steps

### Method 1: Automatic (Git Push)

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Railway auto-deploys** when you push to connected branch

3. **Monitor deployment**:
   - Railway Dashboard → Your service → "Deployments" tab
   - View build logs in real-time

### Method 2: Manual (Railway CLI)

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   # OR
   brew install railway
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Link project**:
   ```bash
   railway link
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

### Build Process

Railway will:
1. Detect Python 3.12 from `runtime.txt`
2. Install dependencies: `pip install -r requirements/base.txt`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Start web service: `daphne -b 0.0.0.0 -p $PORT config.asgi:application`

---

## 🎉 Post-Deployment

### 1. Verify Deployment

```bash
# Check web service
curl https://your-app.railway.app/admin/login/

# Should return 200 OK
```

### 2. Access Admin Panel

```
https://your-app.railway.app/admin/
```

Login with superuser credentials created earlier.

### 3. Test WebSocket Connection

```javascript
// From browser console
const ws = new WebSocket('wss://your-app.railway.app/ws/notifications/');
ws.onopen = () => console.log('Connected!');
```

### 4. Verify Celery Worker

Check Railway Dashboard → Celery Worker service → Logs:
- Should show: `celery@... ready`
- Should show: Connected to redis://...

### 5. Test Email Sending

```bash
railway run python manage.py shell

# In shell:
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Hello', 'noreply@laundryconnect.com', ['test@example.com'])
1
```

---

## 👷 Celery Worker Setup

### Create Worker Service

1. **Railway Dashboard** → "+ New Service"
2. **Select "Empty Service"**
3. **Link to your repo**
4. **Settings**:
   - **Name**: `celery-worker`
   - **Start Command**: `celery -A config worker --loglevel=info --concurrency=2`
   - **Environment Variables**: Same as web service

### Create Beat Service (for scheduled tasks)

1. **Railway Dashboard** → "+ New Service"
2. **Select "Empty Service"**
3. **Link to your repo**
4. **Settings**:
   - **Name**: `celery-beat`
   - **Start Command**: `celery -A config beat --loglevel=info`
   - **Environment Variables**: Same as web service

### Verify Workers

Check logs in Railway Dashboard:
- Worker should show: `celery@worker ready`
- Beat should show: `celery beat v5.x.x is starting`

---

## 📊 Monitoring

### Railway Dashboard

- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Build history and status

### Application Health

Create a health check endpoint (optional):

```python
# config/urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'database': 'connected',
        'redis': 'connected'
    })

urlpatterns = [
    path('health/', health_check),
    # ... rest of URLs
]
```

Access: `https://your-app.railway.app/health/`

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Solution**:
1. Check Railway build logs
2. Verify `requirements/base.txt` syntax
3. Ensure Python 3.12 in `runtime.txt`
4. Check for missing dependencies

### Issue: Database Connection Error

**Solution**:
1. Verify `DATABASE_URL` is set
2. Check PostgreSQL service is running
3. Run migrations: `railway run python manage.py migrate`

### Issue: Static Files Not Loading

**Solution**:
1. Verify `whitenoise` in requirements
2. Check `STATICFILES_STORAGE` in production.py
3. Run: `railway run python manage.py collectstatic`

### Issue: WebSocket Connection Failed

**Solution**:
1. Ensure Daphne is running (check logs)
2. Verify `ASGI_APPLICATION` setting
3. Check Redis connection for channels

### Issue: Celery Worker Not Processing Tasks

**Solution**:
1. Check Celery worker service is running
2. Verify `REDIS_URL` is set correctly
3. Check worker logs for errors
4. Restart worker service

### Issue: ALLOWED_HOSTS Error

**Solution**:
1. Add Railway domain to `ALLOWED_HOSTS`:
   ```bash
   ALLOWED_HOSTS=your-app.railway.app,*.railway.app
   ```
2. Redeploy application

---

## 💰 Cost Estimation

### Railway Pricing (as of 2026)

**Free Tier**:
- $5 credit per month
- Good for development/testing

**Estimated Monthly Cost** (Production):
- **Web Service**: ~$5-10/month
- **PostgreSQL**: ~$5/month
- **Redis**: ~$5/month
- **Celery Worker**: ~$5/month
- **Celery Beat**: ~$5/month
- **Total**: ~$25-30/month

### Cost Optimization

1. **Start with single worker**: Combine Celery worker + beat
2. **Scale later**: Add more workers as traffic grows
3. **Use free tier**: For development environment
4. **Monitor usage**: Railway dashboard shows costs

---

## 🔄 Updates & Redeployment

### Deploy Updates

1. **Push code changes**:
   ```bash
   git add .
   git commit -m "Update feature X"
   git push origin main
   ```

2. **Railway auto-deploys** new version

3. **Zero-downtime**: Railway handles rolling updates

### Manual Restart

Railway Dashboard → Service → "..." → "Restart"

### Rollback

Railway Dashboard → Service → "Deployments" → Select previous → "Rollback"

---

## 📚 Additional Resources

### Railway Documentation
- **Official Docs**: https://docs.railway.app
- **Django Guide**: https://docs.railway.app/guides/django
- **PostgreSQL**: https://docs.railway.app/databases/postgresql
- **Redis**: https://docs.railway.app/databases/redis

### Railway CLI
```bash
# Install
npm i -g @railway/cli

# Common commands
railway login          # Authenticate
railway link           # Link to project
railway up             # Deploy
railway run <cmd>      # Run command
railway logs           # View logs
railway status         # Check status
```

### Support
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app
- **LaundryConnect Issues**: GitHub repository

---

## ✅ Deployment Checklist

Before going live:

### Security
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/HTTPS enabled (`SECURE_SSL_REDIRECT=True`)
- [ ] CSRF and session cookies secure
- [ ] CORS origins properly configured

### Database
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Database backups configured

### Email & Notifications
- [ ] Email backend configured (SendGrid)
- [ ] Twilio SMS configured
- [ ] VAPID keys generated for push notifications
- [ ] Test email sending

### Background Tasks
- [ ] Celery worker running
- [ ] Celery beat running (if using scheduled tasks)
- [ ] Redis connection verified

### Static & Media Files
- [ ] Static files collected
- [ ] WhiteNoise configured
- [ ] Media storage configured (Railway volumes or S3)

### Monitoring
- [ ] Sentry configured (optional)
- [ ] Health check endpoint created
- [ ] Logging configured

### Payment Gateways
- [ ] Razorpay credentials configured
- [ ] Payment webhooks configured
- [ ] Test payment flow

### Mobile App
- [ ] Backend API accessible
- [ ] CORS configured for mobile app
- [ ] Push notifications working
- [ ] WebSocket connections working

---

## 🎊 Success!

Once all checks pass, your LaundryConnect platform is live on Railway!

**Your URLs**:
- **Web App**: `https://your-app.railway.app`
- **Admin Panel**: `https://your-app.railway.app/admin/`
- **API**: `https://your-app.railway.app/api/`
- **WebSocket**: `wss://your-app.railway.app/ws/`

---

## 📝 Notes

### Multiple Environments

Create separate Railway projects for:
- **Development**: Testing new features
- **Staging**: Pre-production testing
- **Production**: Live application

Each with its own:
- Database
- Redis
- Environment variables
- Branch (dev, staging, main)

### Custom Domain

1. **Railway Dashboard** → Your service → "Settings"
2. **Add custom domain**: `app.laundryconnect.com`
3. **Configure DNS**: Add CNAME record
4. **SSL**: Railway auto-generates SSL certificate

---

**Created**: January 11, 2026
**Author**: LaundryConnect Team
**Version**: 1.0

---

Generated with [Claude Code](https://claude.com/claude-code)
