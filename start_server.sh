#!/bin/bash

# LaundryConnect - Server Startup Script
# This script starts the Django development server

echo "========================================"
echo "LaundryConnect - Starting Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not installed in virtual environment!"
    echo "Please install dependencies with: pip install -r requirements.txt"
    exit 1
fi

# Run Django checks
echo "🔍 Running Django configuration checks..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django configuration check failed!"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "========================================"
echo "🚀 Starting Development Server"
echo "========================================"
echo ""
echo "📍 API Documentation:"
echo "   Swagger UI: http://localhost:8000/api/docs/"
echo "   ReDoc:      http://localhost:8000/api/redoc/"
echo ""
echo "📍 Admin Panel:"
echo "   Admin:      http://localhost:8000/admin/"
echo ""
echo "📍 API Endpoints:"
echo "   Accounts:   http://localhost:8000/api/accounts/"
echo "   Services:   http://localhost:8000/api/services/"
echo "   Partners:   http://localhost:8000/api/partners/"
echo "   Payments:   http://localhost:8000/api/payments/"
echo "   Orders:     http://localhost:8000/api/orders/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the Django development server
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver
