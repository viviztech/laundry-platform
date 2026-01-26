# LaundryConnect - Deployment Quick Start
**5-Minute Railway Deployment Guide**

---

## 🚀 Deploy in 5 Minutes

### **Step 1: Prepare Repository (1 min)**

```bash
# Verify deployment files exist
ls railway.json Procfile requirements/base.txt config/settings/production.py

# Commit and push to GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### **Step 2: Deploy to Railway (2 min)**

```bash
# 1. Go to https://railway.app
# 2. Sign up with GitHub (FREE)
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select: laundry-platform
# 5. Wait for deployment (~2 minutes)
```

### **Step 3: Add Databases (1 min)**

```bash
# In Railway Dashboard:
# 1. Click "New" → "Database" → "Add PostgreSQL"
# 2. Click "New" → "Database" → "Add Redis"
# (DATABASE_URL and REDIS_URL are set automatically!)
```

### **Step 4: Set Environment Variables (1 min)**

```bash
# Railway Dashboard → Your Service → Variables → Raw Editor
# Paste this (update SECRET_KEY):

DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-random-secret-key-minimum-50-characters-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app
CORS_ALLOWED_ORIGINS=https://your-app.com
```

### **Step 5: Create Admin User**

```bash
# Railway Dashboard → Your Service → Settings → "Shell"
python manage.py createsuperuser

# Enter:
# Email: admin@laundryconnect.com
# Password: (your secure password)
```

---

## ✅ Verify Deployment

```bash
# Your Railway URL: https://your-app-name.up.railway.app

# Test admin panel:
https://your-app-name.up.railway.app/admin/

# Test API docs:
https://your-app-name.up.railway.app/api/docs/

# Test API health:
curl https://your-app-name.up.railway.app/api/health/
```

---

## 📋 Essential Commands

### **View Logs**
```bash
# Railway Dashboard → Your Service → Deployments → View Logs
```

### **Run Migrations**
```bash
# Railway Shell:
python manage.py migrate
```

### **Load Demo Data**
```bash
# Railway Shell:
python manage.py shell
# Then paste seed_partner_demo_data.py contents
```

### **Restart Application**
```bash
# Railway Dashboard → Your Service → Settings → Restart
```

---

## 🔧 Essential Environment Variables

### **Minimal Configuration (Required)**
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=generate-50-char-random-string
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### **Full Configuration (Recommended)**
```bash
# Core
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key-50-chars-minimum
DEBUG=False
ALLOWED_HOSTS=*.railway.app,yourdomain.com

# Database & Cache (Auto-set by Railway)
# DATABASE_URL=postgresql://... (automatic)
# REDIS_URL=redis://... (automatic)

# CORS (for mobile app)
CORS_ALLOWED_ORIGINS=https://your-mobile-app.com

# Email (SendGrid - FREE 100/day)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Payments (Razorpay TEST mode)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_secret

# SMS (Twilio - optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Error Tracking (Sentry - optional)
SENTRY_DSN=https://xxx@sentry.io/project
```

---

## 🔑 Generate Secret Key

```python
# Run in Python shell:
import secrets
print(secrets.token_urlsafe(50))

# Or online: https://djecrety.ir/
```

---

## 🐛 Troubleshooting

### **Deployment Failed**
```bash
# Check logs: Railway Dashboard → Logs
# Common fixes:

# Missing dependency:
# Add to requirements/base.txt and push

# Database error:
# Verify DATABASE_URL is set (should be automatic)

# Static files error:
# Railway runs collectstatic automatically
# Check STATIC_ROOT in production.py
```

### **500 Error on Admin Page**
```bash
# Check these variables are set:
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=(must be set)
DATABASE_URL=(should be automatic)

# Run migrations:
# Railway Shell → python manage.py migrate
```

### **Cannot Access Admin Panel**
```bash
# 1. Verify deployment is successful (Railway Dashboard)
# 2. Check URL: https://your-app.up.railway.app/admin/
# 3. Create superuser if not done:
#    Railway Shell → python manage.py createsuperuser
```

### **Mobile App Cannot Connect**
```bash
# 1. Verify CORS settings:
CORS_ALLOWED_ORIGINS=https://your-app.com,http://localhost:3000

# 2. Update mobile app API URL:
# mobile/src/constants/api.ts
# BASE_URL: 'https://your-app.up.railway.app/api'

# 3. Test API endpoint:
curl https://your-app.up.railway.app/api/accounts/login/
```

---

## 📊 Free Service Limits

### **Railway**
- ✅ 500 hours/month execution (~20 days)
- ✅ $5 monthly credit
- ✅ 1GB RAM per service
- ✅ 1GB disk storage
- ✅ Unlimited bandwidth

### **Railway PostgreSQL**
- ✅ 5GB storage FREE
- ✅ Shared CPU
- ✅ 512MB RAM
- ✅ Auto-backups included

### **Railway Redis**
- ✅ 100MB storage FREE
- ✅ Shared CPU
- ✅ 512MB RAM

### **Alternative: Neon PostgreSQL**
- ✅ 0.5GB storage
- ✅ Auto-scales to 0 (saves hours)
- ✅ 3GB data transfer/month
- ✅ Perfect for development/testing

### **Alternative: Upstash Redis**
- ✅ 10,000 commands/day
- ✅ 256MB storage
- ✅ Global edge caching
- ✅ Perfect for low-traffic apps

---

## 🔄 Update Deployment

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically:
# 1. Detects push
# 2. Builds new image
# 3. Runs migrations
# 4. Collects static files
# 5. Deploys with zero downtime!
```

---

## 📱 Connect Mobile App

Update mobile app API configuration:

```typescript
// mobile/src/constants/api.ts
export const API_CONFIG = {
  BASE_URL: 'https://your-app.up.railway.app/api',
  TIMEOUT: 30000,
  UPLOAD_TIMEOUT: 60000,
};

export const SOCKET_CONFIG = {
  URL: 'https://your-app.up.railway.app',
};
```

Test connection:
```bash
# From mobile app:
npm start

# Login should work with Railway API!
```

---

## 🎯 Next Steps

1. ✅ **Deploy to Railway** (done!)
2. 🔧 **Create superuser** (admin access)
3. 📊 **Load demo data** (test data)
4. 📱 **Connect mobile app** (update API URL)
5. 🧪 **Test all features** (end-to-end)
6. 🌐 **Add custom domain** (optional)
7. 📧 **Configure SendGrid** (email notifications)
8. 💳 **Set up Razorpay** (test payments)

---

## 📞 Get Help

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **FREE_HOSTING_GUIDE.md**: Detailed deployment guide
- **PARTNER_ADMIN_GUIDE.md**: Admin panel usage guide
- **MOBILE_APP_GUIDE.md**: Mobile app documentation

---

## 💡 Pro Tips

1. **Use Railway CLI for faster deployments**
   ```bash
   npm i -g @railway/cli
   railway login
   railway up
   ```

2. **Monitor logs in real-time**
   ```bash
   railway logs --follow
   ```

3. **Set up custom domain early**
   - Looks more professional
   - Better for mobile app configuration
   - Railway provides FREE SSL

4. **Enable Sentry for error tracking**
   - Catch bugs before users report them
   - 5,000 events/month FREE
   - Essential for production

5. **Backup database regularly**
   - Railway auto-backups included
   - Export manually: Railway Dashboard → Database → Backup

---

**Deployment Time**: ~5 minutes
**Monthly Cost**: $0
**Complexity**: ⭐⭐ (Easy)
**Perfect for**: Partner launch, MVP testing

---

**Last Updated**: January 12, 2026
**Status**: Ready to Deploy! 🚀
