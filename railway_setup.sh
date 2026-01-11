#!/bin/bash
# Railway Setup Script for LaundryConnect Platform
# This script helps verify your deployment is ready

echo "🚂 LaundryConnect Platform - Railway Deployment Checker"
echo "========================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if files exist
echo "📋 Checking deployment files..."
echo ""

files=(
    "Procfile"
    "railway.json"
    "runtime.txt"
    ".railwayignore"
    "requirements/base.txt"
    "config/settings/production.py"
    "config/asgi.py"
)

all_good=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file missing"
        all_good=false
    fi
done

echo ""

# Check requirements
echo "📦 Checking critical dependencies..."
echo ""

dependencies=(
    "django"
    "djangorestframework"
    "daphne"
    "channels"
    "celery"
    "redis"
    "psycopg2-binary"
    "whitenoise"
    "gunicorn"
    "django-unfold"
)

for dep in "${dependencies[@]}"; do
    if grep -q "$dep" requirements/base.txt; then
        echo -e "${GREEN}✓${NC} $dep listed"
    else
        echo -e "${YELLOW}⚠${NC} $dep not found (may be optional)"
    fi
done

echo ""

# Check Python version
echo "🐍 Checking Python version..."
if [ -f "runtime.txt" ]; then
    python_version=$(cat runtime.txt)
    echo -e "${GREEN}✓${NC} Runtime specified: $python_version"
else
    echo -e "${YELLOW}⚠${NC} No runtime.txt found"
fi

echo ""

# Summary
echo "========================================================"
if [ "$all_good" = true ]; then
    echo -e "${GREEN}✅ All critical files present!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Commit all changes: git add . && git commit -m 'Prepare for Railway'"
    echo "2. Push to GitHub: git push origin main"
    echo "3. Go to Railway.app and create new project"
    echo "4. Add PostgreSQL and Redis databases"
    echo "5. Configure environment variables (see .env.railway.example)"
    echo "6. Deploy!"
    echo ""
    echo "📖 Full guide: RAILWAY_DEPLOYMENT_GUIDE.md"
else
    echo -e "${RED}⚠️  Some files are missing!${NC}"
    echo "Please check the errors above and fix them."
fi
echo "========================================================"
