# Railway Deployment - Quick Fix Guide

**For immediate troubleshooting of deployment failures**

---

## 🚨 MOST COMMON ISSUE: Build Command Failure

### Problem
Railway build fails with:
- `collectstatic: command not found`
- `No module named 'django'`
- Build fails before environment variables are loaded

### ✅ IMMEDIATE FIX

The `railway.json` file had a `buildCommand` that runs too early. Here's the fix:

**Updated railway.json** (already fixed in your code):
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

**What changed**:
- ❌ Removed: `"buildCommand": "pip install ..."`
- ✅ Moved migrations and collectstatic to `startCommand`
- ✅ Railway's NIXPACKS will auto-install requirements

---

## 📋 3-Minute Deployment Checklist

### Before Deploying

1. ✅ **Push updated code**:
   ```bash
   git add railway.json nixpacks.toml
   git commit -m "fix: Update Railway configuration"
   git push origin main
   ```

2. ✅ **Verify these files exist**:
   - `runtime.txt` → `python-3.12`
   - `requirements/base.txt` → Has all dependencies
   - `railway.json` → Simplified (no buildCommand)
   - `Procfile` → Has web process definition

### In Railway Dashboard

3. ✅ **Check PostgreSQL is running**
   - Dashboard → PostgreSQL service → Should be 🟢 Active
   - Copy DATABASE_URL from Connect tab

4. ✅ **Check Redis is running**
   - Dashboard → Redis service → Should be 🟢 Active
   - Copy REDIS_URL from Connect tab

5. ✅ **Set REQUIRED environment variables**:
   ```bash
   DJANGO_SETTINGS_MODULE=config.settings.production
   SECRET_KEY=make-this-at-least-50-characters-long-and-random
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   DATABASE_URL=postgresql://... (should be auto-set)
   REDIS_URL=redis://... (should be auto-set)
   ```

6. ✅ **Trigger new deployment**:
   - Settings → "Trigger Deploy"
   - Or push new commit

---

## 🔥 Error → Solution Quick Reference

| Error | Solution |
|-------|----------|
| **"collectstatic not found"** | Remove buildCommand from railway.json |
| **"Application failed to respond"** | Check ALLOWED_HOSTS includes `*.railway.app` |
| **"DATABASES improperly configured"** | Verify DATABASE_URL is set in variables |
| **"No module named X"** | Check requirements/base.txt, trigger rebuild |
| **Admin panel no styling** | Verify whitenoise in requirements, run collectstatic |
| **500 errors** | Check logs: `railway logs` or Dashboard → Logs |
| **Build timeout** | Simplify railway.json, use nixpacks.toml |
| **Redis connection failed** | Verify REDIS_URL is set |

---

## 🎯 Step-by-Step: Fix & Redeploy (5 Minutes)

### Step 1: Update Configuration (Done ✅)
Files already updated in your project:
- ✅ `railway.json` - Simplified
- ✅ `nixpacks.toml` - Alternative config
- ✅ `RAILWAY_TROUBLESHOOTING_GUIDE.md` - Full guide

### Step 2: Push Updated Code

```bash
git add railway.json nixpacks.toml RAILWAY_TROUBLESHOOTING_GUIDE.md RAILWAY_QUICK_FIX.md
git commit -m "fix: Simplify Railway build process for successful deployment"
git push origin main
```

### Step 3: In Railway Dashboard

1. **Go to your project**: https://railway.app/project/your-project

2. **Click web service** (Django app)

3. **Check Variables tab**:
   - ✅ `DATABASE_URL` exists (from PostgreSQL service)
   - ✅ `REDIS_URL` exists (from Redis service)
   - ✅ `DJANGO_SETTINGS_MODULE=config.settings.production`
   - ✅ `SECRET_KEY` is set (50+ characters)
   - ✅ `ALLOWED_HOSTS=*.railway.app`

4. **Trigger new deployment**:
   - Settings tab → Scroll down
   - Click **"Trigger Deploy"** button
   - Or just push new commit (auto-deploys)

5. **Watch deployment logs**:
   - Deployments tab → Click latest deployment
   - Should see:
     ```
     ✓ Installing dependencies
     ✓ Running migrations
     ✓ Collecting static files
     ✓ Starting Daphne server
     ✓ Deployment successful
     ```

### Step 4: Access Your App

1. Get Railway URL:
   - Settings → Domains section
   - Copy: `https://your-app-name.up.railway.app`

2. Update ALLOWED_HOSTS:
   ```bash
   ALLOWED_HOSTS=your-app-name.up.railway.app,*.railway.app
   ```

3. Access admin:
   ```
   https://your-app-name.up.railway.app/admin/
   ```

---

## 🆘 Still Failing?

### Check Build Logs

**Railway Dashboard**:
1. Click web service
2. Deployments tab
3. Click failed deployment
4. Read error message (usually at the end)

**Railway CLI**:
```bash
railway logs
```

### Common Log Errors

**"No such file: requirements/base.txt"**
- Solution: Check file path is correct
- Verify: `ls requirements/base.txt`

**"Port 8000 already in use"**
- Solution: Use Railway's $PORT variable
- Check startCommand: `daphne -b 0.0.0.0 -p $PORT`

**"Failed to bind to 0.0.0.0:$PORT"**
- Solution: Daphne needs explicit IP binding
- Check: `daphne -b 0.0.0.0 -p $PORT` (not just `-p $PORT`)

---

## 📞 Get Help

### Railway Community

**Railway Discord** (Fastest help): https://discord.gg/railway
- #help channel
- Very responsive community
- Railway team members active

**Railway Docs**: https://docs.railway.app
- Python guide: https://docs.railway.app/guides/python
- Django guide: https://docs.railway.app/guides/django

### Share These When Asking for Help

1. **Error message** (from deployment logs)
2. **railway.json** content
3. **Start command** being used
4. **Environment variables** (redact secrets!)

---

## ✅ Success Indicators

Your deployment is successful when you see:

- [ ] Build completes without errors (green ✓)
- [ ] Service shows 🟢 **Active** status
- [ ] Railway URL is accessible
- [ ] `/admin/` shows Django Unfold login page
- [ ] Admin panel has styling (not plain HTML)
- [ ] No errors in deployment logs

---

## 🎉 What to Do After Successful Deployment

### 1. Run Initial Setup

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link
railway login
railway link

# Run migrations (if not auto-ran)
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Load notification templates
railway run python manage.py load_notification_templates
```

### 2. Test Your App

- ✅ Access admin panel
- ✅ Login with superuser
- ✅ Check Django Unfold UI loads
- ✅ Test API endpoints
- ✅ Verify database connection

### 3. Setup Celery Worker (Optional)

See full guide: [RAILWAY_TROUBLESHOOTING_GUIDE.md](RAILWAY_TROUBLESHOOTING_GUIDE.md#optional-setup-celery-worker)

---

**Last Updated**: January 11, 2026
**Status**: Ready to deploy

---

Generated with [Claude Code](https://claude.com/claude-code)
