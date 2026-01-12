# LaundryConnect - FREE Hosting Guide
**Partner Launch - $0/month Deployment Strategy**

---

## 🎯 Overview

This guide shows you how to deploy LaundryConnect's admin panel and API using **100% FREE services** - perfect for partner launch, testing, and initial operations.

### **Total Monthly Cost: $0** 💰

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Free Hosting Stack                    │
├─────────────────────────────────────────────────────────┤
│  Web Server:     Railway (500 hrs/month FREE)            │
│  Database:       Neon PostgreSQL (0.5GB FREE)            │
│  Cache/Queue:    Upstash Redis (10K cmds/day FREE)       │
│  Static Files:   WhiteNoise (bundled with Django)        │
│  Media Storage:  Cloudflare R2 (10GB FREE)               │
│  Email:          SendGrid (100 emails/day FREE)          │
│  Monitoring:     Railway Logs (FREE)                     │
│  Error Tracking: Sentry (5K events/month FREE)           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚂 Option 1: Railway (Recommended)

**Free Tier:** 500 hours/month (~20 days continuous) + $5 credit

### **Step 1: Prepare Your Repository**

```bash
# Ensure all deployment files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### **Step 2: Create Railway Account**

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub (FREE)
3. Verify your account

### **Step 3: Deploy Django Application**

```bash
# 1. Create new project on Railway
# Click "New Project" → "Deploy from GitHub repo"

# 2. Select your laundry-platform repository

# 3. Railway will automatically:
#    - Detect Python/Django app
#    - Read railway.json configuration
#    - Install dependencies from requirements/base.txt
#    - Run migrations
#    - Collect static files
```

### **Step 4: Add PostgreSQL Database**

```bash
# In Railway Dashboard:
# 1. Click "New" → "Database" → "Add PostgreSQL"
# 2. Railway automatically sets DATABASE_URL environment variable
# 3. No configuration needed - Django will auto-connect!
```

### **Step 5: Add Redis**

```bash
# In Railway Dashboard:
# 1. Click "New" → "Database" → "Add Redis"
# 2. Railway automatically sets REDIS_URL environment variable
# 3. Celery and Channels will auto-connect!
```

### **Step 6: Configure Environment Variables**

Go to Railway Dashboard → Your Service → Variables → Raw Editor:

```bash
# Essential Variables
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-change-this-minimum-50-chars
DEBUG=False
ALLOWED_HOSTS=*.railway.app

# CORS (for mobile app)
CORS_ALLOWED_ORIGINS=https://your-mobile-app-domain.com

# Email (SendGrid - see below)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Payment (Razorpay test mode - FREE)
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_test_secret
```

### **Step 7: Deploy & Verify**

```bash
# Railway auto-deploys on every git push!

# Check deployment:
# 1. Go to Railway Dashboard → Deployments
# 2. Click latest deployment → View Logs
# 3. Wait for "Application startup complete"

# Get your URL:
# Railway provides: https://your-app.up.railway.app

# Test endpoints:
curl https://your-app.up.railway.app/admin/
curl https://your-app.up.railway.app/api/docs/
```

### **Step 8: Create Superuser**

```bash
# In Railway Dashboard:
# 1. Click your service → Settings → "Shell"
# 2. Run: python manage.py createsuperuser
# 3. Enter email and password
# 4. Access: https://your-app.up.railway.app/admin/
```

---

## 🗄️ Database Setup: Neon PostgreSQL

**If Railway's PostgreSQL isn't enough, use Neon (0.5GB FREE forever)**

### **Step 1: Create Neon Account**

1. Go to [Neon.tech](https://neon.tech)
2. Sign up with GitHub (FREE)
3. Create new project: "laundryconnect-db"

### **Step 2: Get Connection String**

```bash
# Neon Dashboard → Connection Details → Copy connection string
# Format: postgresql://user:pass@host/dbname?sslmode=require

# Example:
postgresql://ganesh:AbC123xyz@ep-cool-name-123456.us-east-2.aws.neon.tech/laundryconnect?sslmode=require
```

### **Step 3: Add to Railway**

```bash
# Railway Dashboard → Variables → Add Variable:
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
```

---

## 🔴 Redis Setup: Upstash

**10,000 commands/day FREE (enough for partner launch)**

### **Step 1: Create Upstash Account**

1. Go to [Upstash.com](https://upstash.com)
2. Sign up with GitHub (FREE)
3. Create Redis database: "laundryconnect-redis"

### **Step 2: Get Connection URL**

```bash
# Upstash Dashboard → Your Database → REST API → Redis URL
# Copy both formats:

# TLS URL (recommended):
rediss://default:AbC123xyz@host-12345.upstash.io:6379

# Non-TLS URL (if needed):
redis://default:AbC123xyz@host-12345.upstash.io:6379
```

### **Step 3: Add to Railway**

```bash
# Railway Dashboard → Variables → Add Variable:
REDIS_URL=rediss://default:AbC123xyz@host-12345.upstash.io:6379
```

---

## 📧 Email Setup: SendGrid

**100 emails/day FREE (enough for initial testing)**

### **Step 1: Create SendGrid Account**

1. Go to [SendGrid.com](https://sendgrid.com)
2. Sign up (FREE tier)
3. Verify your email

### **Step 2: Create API Key**

```bash
# SendGrid Dashboard:
# 1. Settings → API Keys → Create API Key
# 2. Name: "LaundryConnect-Railway"
# 3. Permissions: "Full Access"
# 4. Copy the key (shown only once!)
```

### **Step 3: Configure Railway**

```bash
# Railway Dashboard → Variables:
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## 🖼️ Media Files: Cloudflare R2

**10GB storage FREE (more than enough for images)**

### **Option A: Use Railway Volumes (Simpler)**

```bash
# Railway Dashboard → Your Service → Settings → Volumes
# 1. Click "Add Volume"
# 2. Mount path: /app/media
# 3. Size: 1GB (FREE with Railway)

# In Railway Variables:
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
```

### **Option B: Cloudflare R2 (Scalable)**

```bash
# 1. Go to Cloudflare Dashboard
# 2. R2 → Create bucket: "laundryconnect-media"
# 3. Get Access Key ID and Secret
# 4. Configure in Railway:

AWS_ACCESS_KEY_ID=your-r2-access-key
AWS_SECRET_ACCESS_KEY=your-r2-secret-key
AWS_STORAGE_BUCKET_NAME=laundryconnect-media
AWS_S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
AWS_S3_REGION_NAME=auto
USE_S3_STORAGE=True
```

---

## 📱 SMS Setup: Twilio

**Free trial: $15.50 credit + 1 free phone number**

### **Step 1: Create Twilio Account**

1. Go to [Twilio.com](https://www.twilio.com/try-twilio)
2. Sign up (FREE trial)
3. Verify your phone number

### **Step 2: Get Credentials**

```bash
# Twilio Console → Account Info:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token

# Phone Numbers → Get a free number:
TWILIO_PHONE_NUMBER=+1234567890
```

### **Step 3: Add to Railway**

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_STATUS_CALLBACK_URL=https://your-app.railway.app/api/sms/callback/
```

---

## 🐛 Error Tracking: Sentry

**5,000 events/month FREE**

### **Step 1: Create Sentry Account**

1. Go to [Sentry.io](https://sentry.io)
2. Sign up with GitHub (FREE)
3. Create project: "laundryconnect-api"

### **Step 2: Get DSN**

```bash
# Sentry Dashboard → Settings → Client Keys (DSN)
# Copy DSN: https://abc123@o123456.ingest.sentry.io/7891011
```

### **Step 3: Add to Railway**

```bash
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/7891011
```

---

## ⚡ Quick Deployment Checklist

### **Pre-Deployment** ✅

- [ ] All code committed to GitHub
- [ ] `.env` added to `.gitignore`
- [ ] `railway.json` configured
- [ ] `Procfile` present
- [ ] `requirements/base.txt` up to date
- [ ] `config/settings/production.py` verified

### **Railway Setup** ✅

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] PostgreSQL database added
- [ ] Redis database added
- [ ] Environment variables configured
- [ ] Deployment successful

### **External Services** ✅

- [ ] SendGrid API key configured
- [ ] Twilio credentials (if using SMS)
- [ ] Razorpay test keys configured
- [ ] Sentry DSN configured (optional)

### **Post-Deployment** ✅

- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] API docs accessible (`/api/docs/`)
- [ ] Demo data loaded
- [ ] Test login works
- [ ] Test order creation works
- [ ] Email sending works
- [ ] WebSocket connection works

---

## 🔧 Deployment Commands

### **Run Migrations**

```bash
# Railway Dashboard → Service → Shell
python manage.py migrate
```

### **Create Superuser**

```bash
python manage.py createsuperuser
```

### **Load Demo Data**

```bash
python manage.py shell < seed_partner_demo_data.py
```

### **Collect Static Files** (automatic)

```bash
# Runs automatically on deployment
python manage.py collectstatic --noinput
```

### **Check Deployment**

```bash
# View logs
railway logs

# Check health
curl https://your-app.railway.app/api/health/

# Test admin
curl https://your-app.railway.app/admin/login/
```

---

## 🌐 Custom Domain (Optional)

### **Using Railway**

```bash
# Railway Dashboard → Service → Settings → Domains
# 1. Click "Generate Domain" (FREE subdomain)
# 2. Or add custom domain:
#    - Click "Custom Domain"
#    - Add: api.yourdomain.com
#    - Update DNS: CNAME → your-app.railway.app

# Update ALLOWED_HOSTS:
ALLOWED_HOSTS=api.yourdomain.com,*.railway.app
```

---

## 🔄 Continuous Deployment

Railway automatically deploys on every `git push`:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically:
# 1. Detects push
# 2. Builds new image
# 3. Runs tests
# 4. Deploys if successful
# 5. Zero downtime deployment!
```

---

## 📊 Monitoring & Logs

### **View Real-time Logs**

```bash
# Railway Dashboard → Your Service → Logs
# Or use Railway CLI:
railway logs --follow
```

### **Monitor Performance**

```bash
# Railway Dashboard → Metrics
# Shows:
# - CPU usage
# - Memory usage
# - Request count
# - Response times
```

### **Set Up Alerts**

```bash
# Sentry Dashboard → Alerts
# Configure:
# - Error rate threshold
# - Performance issues
# - Email/Slack notifications
```

---

## 🚨 Troubleshooting

### **Deployment Failed**

```bash
# Check logs in Railway Dashboard → Logs
# Common issues:

# 1. Missing dependencies
# Fix: Add to requirements/base.txt

# 2. Migration errors
# Fix: Railway Shell → python manage.py migrate --fake

# 3. Static files not loading
# Fix: Check STATIC_ROOT and collectstatic

# 4. Database connection error
# Fix: Verify DATABASE_URL is set correctly
```

### **Application Not Starting**

```bash
# Check Procfile is correct:
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application

# Verify PORT is set by Railway (automatic)
# Check production settings are loaded:
DJANGO_SETTINGS_MODULE=config.settings.production
```

### **Redis Connection Error**

```bash
# Verify REDIS_URL format:
# Should be: redis://default:pass@host:6379
# Or: rediss://default:pass@host:6379 (TLS)

# Test connection in Railway Shell:
python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

---

## 💡 Cost Optimization Tips

### **Railway Free Tier Limits**

```
✅ 500 execution hours/month
✅ $5 monthly credit
✅ 1GB RAM per service
✅ 1GB disk storage

# To stay within limits:
1. Deploy only when needed (not 24/7 initially)
2. Use sleep mode for non-peak hours
3. Optimize worker processes (use 1-2 workers)
4. Monitor usage in Railway Dashboard
```

### **Database Optimization**

```bash
# Use Neon's free tier:
✅ 0.5GB storage
✅ Auto-scales to 0 when idle
✅ 3GB data transfer/month

# Tips:
1. Regular cleanup of old data
2. Archive old orders
3. Delete unused images
4. Use indexes on frequently queried fields
```

### **Redis Optimization**

```bash
# Upstash free tier:
✅ 10,000 commands/day
✅ 256MB storage

# Tips:
1. Set short TTL for cache (1-5 minutes)
2. Limit Celery task retention
3. Use database for persistent data
4. Monitor command count in Upstash dashboard
```

---

## 🎯 Alternative Free Hosting Options

### **Option 2: Render**

**Free Tier:** 750 hours/month

```yaml
# render.yaml (already included)
services:
  - type: web
    name: laundryconnect-api
    env: python
    plan: free
    buildCommand: pip install -r requirements/base.txt && python manage.py migrate
    startCommand: daphne config.asgi:application

databases:
  - name: laundryconnect-db
    plan: free
    databaseName: laundryconnect
```

**Deploy to Render:**
1. Sign up at [Render.com](https://render.com)
2. Connect GitHub repo
3. Add PostgreSQL database (FREE)
4. Add Redis (need paid plan or use Upstash)
5. Configure environment variables

### **Option 3: Fly.io**

**Free Tier:** 3 shared VMs + 3GB storage

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch
fly deploy
```

---

## 📖 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Neon Docs**: https://neon.tech/docs
- **Upstash Docs**: https://docs.upstash.com
- **SendGrid Docs**: https://docs.sendgrid.com
- **Sentry Docs**: https://docs.sentry.io

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Admin panel loads: `https://your-app.railway.app/admin/`
- [ ] API docs load: `https://your-app.railway.app/api/docs/`
- [ ] Can login to admin panel
- [ ] Partners page shows data
- [ ] Orders page shows data
- [ ] Services page shows data
- [ ] Can create new order from admin
- [ ] Email sending works (test from admin)
- [ ] Mobile app can connect to API
- [ ] WebSocket chat works
- [ ] Payment test mode works

---

## 🎉 Next Steps After Deployment

1. **Test thoroughly** with partner accounts
2. **Load demo data** for realistic testing
3. **Share admin URL** with team members
4. **Test mobile app** connection
5. **Monitor logs** for first 24 hours
6. **Set up custom domain** (optional)
7. **Configure backups** (Railway auto-backups included)
8. **Plan for scaling** when usage grows

---

## 📞 Support

If you encounter issues:

1. Check Railway logs first
2. Review this guide's troubleshooting section
3. Check Railway status page
4. Join Railway Discord community
5. Review Django deployment best practices

---

**Total Setup Time:** ~30-45 minutes
**Monthly Cost:** $0 (for partner launch)
**Supports:** 50-100 concurrent users easily

**Perfect for:** Partner launch, testing, MVP validation

---

**Last Updated**: January 12, 2026
**Deployment Target**: Railway (Primary) + Free Services
**Status**: Production Ready ✅
