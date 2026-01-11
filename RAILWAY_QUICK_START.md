# Railway Deployment - Quick Start Guide

**Estimated Time**: 15-20 minutes
**Difficulty**: Beginner-friendly

---

## 🚀 Deploy in 5 Steps

### Step 1: Push to GitHub (2 min)

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project (3 min)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `laundry-platform` repository
5. Select `main` branch

**Railway will start building automatically!**

### Step 3: Add Databases (2 min)

In your Railway project:

**Add PostgreSQL**:
- Click "+ New"
- Select "Database"
- Choose "PostgreSQL"
- Wait for provisioning (~30 seconds)

**Add Redis**:
- Click "+ New"
- Select "Database"
- Choose "Redis"
- Wait for provisioning (~30 seconds)

### Step 4: Configure Environment Variables (5 min)

1. Click your **web service**
2. Go to **"Variables"** tab
3. Click **"Raw Editor"**
4. Copy from [.env.railway.example](.env.railway.example) and paste
5. Update these critical values:

```bash
SECRET_KEY=your-super-secret-key-change-this
ALLOWED_HOSTS=your-app-name.railway.app,*.railway.app
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

6. Click **"Save"**

### Step 5: Run Migrations (3 min)

Once deployed:

1. Click your web service
2. Click "..." menu → "Run Command"
3. Run these commands one by one:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## ✅ You're Live!

Your app is now running at: `https://your-app-name.railway.app`

**Admin Panel**: `https://your-app-name.railway.app/admin/`

---

## 🎯 Optional: Setup Celery Worker

For background tasks (emails, SMS, notifications):

1. Click "+ New" in Railway
2. Select "Empty Service"
3. Link to same repository
4. Set **Start Command**:
   ```
   celery -A config worker --loglevel=info
   ```
5. Copy **all environment variables** from web service
6. Deploy

---

## 📊 Estimated Costs

**Monthly (Production)**:
- Web Service: $5-10
- PostgreSQL: $5
- Redis: $5
- Celery Worker: $5
- **Total: ~$20-25/month**

**Free Tier**: $5 credit/month (good for testing)

---

## 🐛 Quick Troubleshooting

**Build fails?**
- Check Railway logs for errors
- Verify `requirements/base.txt` is correct

**Can't access admin?**
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

**500 errors?**
- Check `ALLOWED_HOSTS` includes your Railway domain
- Verify `DATABASE_URL` is set
- Check service logs for details

**Static files missing?**
- Run: `python manage.py collectstatic --noinput`
- Verify `whitenoise` in requirements

---

## 📚 Full Documentation

For detailed instructions, see [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)

---

## 🎉 What You Get

✅ Django 6.0 with Unfold Admin UI
✅ WebSocket support (real-time features)
✅ PostgreSQL database
✅ Redis caching/queue
✅ Celery background workers
✅ SSL/HTTPS enabled
✅ Static files served via WhiteNoise
✅ Production-ready configuration

---

**Need Help?**
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
- Full Guide: [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)

---

Generated with [Claude Code](https://claude.com/claude-code)
