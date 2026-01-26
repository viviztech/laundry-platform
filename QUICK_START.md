# LaundryConnect - Quick Start Guide

## 🚀 Running the Application

### Method 1: Using the Startup Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x start_server.sh

# Run the server
./start_server.sh
```

### Method 2: Manual Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations (first time or after model changes)
python manage.py migrate

# Create superuser (first time only)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

## 📱 Accessing the Application

Once the server is running, you can access:

### 1. Admin Panel (Django Admin)
**URL**: http://localhost:8000/admin/

**What you can do:**
- ✅ Manage all data (users, orders, payments, partners, services)
- ✅ View and edit database records
- ✅ Process refunds
- ✅ Verify partners
- ✅ Configure pricing zones

**Login**: Use the superuser credentials you created

**Available Sections:**
- **Accounts**: Users, Addresses
- **Services**: Categories, Items, Pricing Zones, Pricing Tiers
- **Orders**: Orders, Order Items, Order Status History
- **Partners**: Partners, Service Areas, Availability, Holidays, Performance
- **Payments**: Payments, Wallets, Wallet Transactions, Refunds, Payment Methods

### 2. API Documentation (Interactive)

#### Swagger UI (Recommended for Testing)
**URL**: http://localhost:8000/api/docs/

**Features:**
- ✅ Interactive API testing
- ✅ Try out all endpoints
- ✅ See request/response examples
- ✅ Automatic authentication handling

**How to use:**
1. Click the "Authorize" button (top right)
2. Enter your JWT token: `Bearer <your-access-token>`
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"
7. See the response below

#### ReDoc (Better for Reading)
**URL**: http://localhost:8000/api/redoc/

**Features:**
- ✅ Clean, readable documentation
- ✅ Easy to navigate
- ✅ Shows all models and schemas
- ✅ Better for understanding the API structure

### 3. API Endpoints (Direct Access)

All endpoints are under `/api/`:

```
Accounts:
  POST   /api/accounts/register/           - Register new user
  POST   /api/accounts/login/              - Login (get JWT token)
  POST   /api/accounts/token/refresh/      - Refresh access token
  GET    /api/accounts/profile/            - Get current user profile
  POST   /api/accounts/addresses/          - Add new address

Services:
  GET    /api/services/categories/         - List service categories
  GET    /api/services/items/              - List service items
  GET    /api/services/pricing-zones/      - List pricing zones
  GET    /api/services/pricing-tiers/      - List pricing tiers

Orders:
  GET    /api/orders/                      - List user's orders
  POST   /api/orders/                      - Create new order
  GET    /api/orders/{id}/                 - Get order details
  POST   /api/orders/{id}/cancel/          - Cancel order
  POST   /api/orders/{id}/assign/          - Assign partner (admin)

Partners:
  GET    /api/partners/partners/           - List partners
  POST   /api/partners/partners/           - Register as partner
  POST   /api/partners/partners/{id}/update_status/  - Update status (admin)
  POST   /api/partners/partners/{id}/verify/         - Verify partner (admin)
  GET    /api/partners/partners/available/ - Get available partners

Payments:
  GET    /api/payments/payments/           - List payments
  POST   /api/payments/payments/           - Create payment
  POST   /api/payments/payments/{id}/verify/        - Verify payment
  GET    /api/payments/wallets/            - Get wallet
  POST   /api/payments/wallets/{id}/add_balance/    - Add wallet balance
  GET    /api/payments/refunds/            - List refunds
  POST   /api/payments/refunds/            - Request refund
  POST   /api/payments/payment-methods/    - Add payment method
```

## 🔐 Authentication

### Getting a JWT Token

```bash
# Register a new user
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "user_type": "customer"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Response will include:
# {
#   "access": "eyJ0eXAiOiJKV1...",  <- Use this token
#   "refresh": "eyJ0eXAiOiJKV1..."
# }
```

### Using the Token

```bash
# Add to Authorization header
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..."
```

## 🎯 Common Tasks

### 1. Create a Superuser (Admin Access)

```bash
source venv/bin/activate
python manage.py createsuperuser

# Follow the prompts:
# Email: admin@laundryconnect.com
# Password: (your secure password)
# First name: Admin
# Last name: User
```

### 2. Create Sample Data

```bash
# Option 1: Through Django Admin
# - Visit http://localhost:8000/admin/
# - Manually create records

# Option 2: Using Django Shell
python manage.py shell

# Then run:
from apps.accounts.models import User
from apps.services.models import ServiceCategory, PricingZone
from decimal import Decimal

# Create a pricing zone
zone = PricingZone.objects.create(
    name="Mumbai Central",
    description="Central Mumbai area",
    base_multiplier=Decimal('1.0')
)

# Create a service category
category = ServiceCategory.objects.create(
    name="Wash & Fold",
    description="Regular washing and folding service",
    icon="wash-icon.png",
    is_active=True
)
```

### 3. Run Migrations

```bash
source venv/bin/activate

# Create migration files (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### 4. Test the Payment APIs

```bash
# 1. Get authentication token (see above)
export TOKEN="your-access-token-here"

# 2. Add a payment method
curl -X POST http://localhost:8000/api/payments/payment-methods/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "upi",
    "nickname": "My UPI",
    "upi_id": "user@paytm",
    "is_default": true,
    "card_token": ""
  }'

# 3. Create a payment (needs an order first)
curl -X POST http://localhost:8000/api/payments/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-uuid-here",
    "payment_method": "upi",
    "gateway": "razorpay"
  }'
```

## 🛠️ Development Workflow

### 1. Start Fresh Development Session

```bash
# Navigate to project
cd /Users/ganeshthangavel/projects/laundry-platform

# Activate virtual environment
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Apply any new migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### 2. Make Changes to Models

```bash
# 1. Edit your model in apps/*/models.py

# 2. Create migration
python manage.py makemigrations

# 3. Apply migration
python manage.py migrate

# 4. Restart server (Ctrl+C then python manage.py runserver)
```

### 3. Debug Issues

```bash
# Check for errors
python manage.py check

# View SQL for a migration
python manage.py sqlmigrate app_name migration_number

# Open Django shell
python manage.py shell

# Access database directly
python manage.py dbshell
```

## 📊 Monitoring

### View Server Logs
The Django development server shows logs in the terminal:
- Request logs (GET, POST, etc.)
- Error messages
- SQL queries (if DEBUG=True)

### Common Log Messages

```
✅ Good:
[02/Jan/2026 10:00:00] "GET /api/orders/ HTTP/1.1" 200 1234
[02/Jan/2026 10:00:01] "POST /api/payments/payments/ HTTP/1.1" 201 567

⚠️ Warnings:
[02/Jan/2026 10:00:02] "GET /api/orders/999/ HTTP/1.1" 404 89
[02/Jan/2026 10:00:03] "POST /api/payments/payments/ HTTP/1.1" 400 123

❌ Errors:
[02/Jan/2026 10:00:04] "GET /api/orders/ HTTP/1.1" 500 45
```

## 🔧 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
python manage.py runserver 8080
```

### Database errors

```bash
# Reset database (WARNING: deletes all data)
python manage.py flush

# Or drop and recreate database
# Then run: python manage.py migrate
```

### Module not found errors

```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Permission errors in Admin

```bash
# Make user a superuser
python manage.py shell
from apps.accounts.models import User
user = User.objects.get(email='user@example.com')
user.is_staff = True
user.is_superuser = True
user.save()
```

## 📚 Next Steps

1. **Explore Admin Panel**: http://localhost:8000/admin/
   - Create test data
   - Understand the data structure

2. **Test APIs with Swagger**: http://localhost:8000/api/docs/
   - Try different endpoints
   - See request/response formats

3. **Review Documentation**:
   - See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed API testing
   - See [PHASE_4_SUMMARY.md](PHASE_4_SUMMARY.md) for payment features

4. **Build Frontend**:
   - Use the APIs to build a React/Vue/Angular frontend
   - Or use the admin panel as your UI

5. **Add Real Payment Gateway**:
   - Integrate Razorpay/Stripe
   - Handle webhooks
   - Test actual payments

## 🎉 You're Ready!

The server is now running and you can:
- ✅ Access the admin panel
- ✅ Test APIs with Swagger UI
- ✅ Create and manage data
- ✅ Process payments and refunds
- ✅ Manage partners and orders

Happy coding! 🚀
