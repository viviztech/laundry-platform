# 🚀 How to Run LaundryConnect Platform

## Quick Start (3 Simple Steps)

### Step 1: Activate Virtual Environment
```bash
cd /Users/ganeshthangavel/projects/laundry-platform
source venv/bin/activate
```

### Step 2: Start the Server
```bash
# Use the startup script (recommended)
./start_server.sh

# OR run manually
python manage.py runserver
```

### Step 3: Access the Application
Open your browser and visit:
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📱 What You Can Access

### 1. Swagger UI - Interactive API Testing
**URL**: http://localhost:8000/api/docs/

**Perfect for**:
- Testing all API endpoints interactively
- Trying out the payment APIs
- Understanding request/response formats
- No need to write code or cURL commands

**How to use**:
1. Click "Authorize" button (top right, green lock icon)
2. Enter: `Bearer your-token-here` (get token from login endpoint)
3. Click any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"
7. See the response immediately

### 2. Admin Panel - Data Management
**URL**: http://localhost:8000/admin/

**Perfect for**:
- Managing all database records
- Creating test data
- Processing refunds
- Verifying partners
- Viewing payment transactions

**Login**:
First create a superuser:
```bash
source venv/bin/activate
python manage.py createsuperuser
# Follow the prompts
```

**What you can manage**:
- **Accounts**: Users, Addresses, Profiles
- **Services**: Categories, Items, Pricing Zones, Pricing Tiers
- **Orders**: Orders, Order Items, Status History
- **Partners**: Partners, Service Areas, Availability, Performance
- **Payments**: Payments, Wallets, Transactions, Refunds, Payment Methods

### 3. ReDoc - API Documentation
**URL**: http://localhost:8000/api/redoc/

**Perfect for**:
- Reading comprehensive API documentation
- Understanding the entire API structure
- Viewing all models and schemas
- Sharing with frontend developers

---

## 🎯 Common Tasks

### Testing the Payment System

#### 1. Add a Payment Method (via Swagger UI)
1. Go to http://localhost:8000/api/docs/
2. Authorize with your token
3. Find `POST /api/payments/payment-methods/`
4. Click "Try it out"
5. Use this sample data:
```json
{
  "type": "upi",
  "nickname": "My PhonePe",
  "upi_id": "user@phonepe",
  "is_default": true,
  "card_token": ""
}
```
6. Click "Execute"
7. See your saved payment method!

#### 2. Check Your Wallet
1. In Swagger UI, find `GET /api/payments/wallets/`
2. Click "Try it out" → "Execute"
3. View your wallet balance

#### 3. Add Money to Wallet
1. Find `POST /api/payments/wallets/{id}/add_balance/`
2. Enter your wallet ID
3. Use this data:
```json
{
  "amount": "500.00",
  "description": "Adding test balance"
}
```
4. Execute and check your new balance

### Creating Test Data (via Admin Panel)

#### 1. Create a Service Category
1. Go to http://localhost:8000/admin/
2. Navigate to "Services" → "Service categories"
3. Click "Add service category"
4. Fill in:
   - Name: "Wash & Fold"
   - Description: "Regular washing and folding"
   - Icon: "wash-icon.png"
   - Is active: ✓
5. Save

#### 2. Create a Pricing Zone
1. Go to "Services" → "Pricing zones"
2. Click "Add pricing zone"
3. Fill in:
   - Name: "Mumbai Central"
   - Description: "Central Mumbai area"
   - Base multiplier: 1.0
4. Save

#### 3. Create an Order
1. Go to "Orders" → "Orders"
2. Click "Add order"
3. Select user, service zone, address
4. Add order items
5. Save

---

## 🔧 Troubleshooting

### Problem: Virtual environment not found
```bash
# Create it
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt
```

### Problem: Django not installed
```bash
source venv/bin/activate
pip install -r requirements/development.txt
```

### Problem: Port 8000 already in use
```bash
# Find what's using it
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
python manage.py runserver 8080
```

### Problem: Database not configured
```bash
# Create PostgreSQL database
createdb laundry_db

# Update .env file with credentials
# Then run migrations
python manage.py migrate
```

### Problem: Can't login to admin
```bash
# Create a superuser
source venv/bin/activate
python manage.py createsuperuser

# Follow prompts:
# Email: admin@example.com
# Password: (choose a strong password)
```

### Problem: Token authentication not working
```bash
# Get a fresh token:
# 1. Go to http://localhost:8000/api/docs/
# 2. Find POST /api/accounts/login/
# 3. Try it out with your credentials
# 4. Copy the "access" token from response
# 5. Click "Authorize" and paste: Bearer <token>
```

---

## 📊 Server Status Checks

### Verify Everything is Working
```bash
source venv/bin/activate

# Check Django configuration
python manage.py check

# Check database connection
python manage.py dbshell
# Type: \q to exit

# View all migrations
python manage.py showmigrations

# Run migrations if needed
python manage.py migrate
```

### View Server Logs
When the server is running, you'll see logs like:
```
[02/Jan/2026 10:00:00] "GET /api/orders/ HTTP/1.1" 200 1234
[02/Jan/2026 10:00:01] "POST /api/payments/payments/ HTTP/1.1" 201 567
```

- **200**: Success (GET request)
- **201**: Created (POST request)
- **400**: Bad Request (client error)
- **401**: Unauthorized (missing/invalid token)
- **404**: Not Found
- **500**: Server Error

---

## 🎨 Frontend Development

### API Base URL
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Authentication Example
```javascript
// Login
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/accounts/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data;
};

// Make authenticated request
const getOrders = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/orders/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

---

## 📚 Additional Resources

- **Testing Guide**: See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions
- **Payment Guide**: See [PHASE_4_SUMMARY.md](PHASE_4_SUMMARY.md) for payment system details
- **Full README**: See [README.md](README.md) for complete project documentation

---

## ✅ Success Checklist

Before you start developing, make sure:

- [ ] Virtual environment is activated (`source venv/bin/activate`)
- [ ] Server is running (`./start_server.sh` or `python manage.py runserver`)
- [ ] You can access http://localhost:8000/api/docs/
- [ ] You can access http://localhost:8000/admin/
- [ ] You have a superuser account created
- [ ] You've tested at least one API endpoint in Swagger UI
- [ ] You understand how to get an authentication token

---

## 🎉 You're All Set!

Your LaundryConnect platform is now running with:
- ✅ Complete REST APIs
- ✅ Payment integration (Razorpay/Stripe ready)
- ✅ Wallet system
- ✅ Partner management
- ✅ Order management
- ✅ Interactive API documentation
- ✅ Admin panel for data management

**Need help?** Check the other documentation files or the inline comments in the code.

**Happy coding! 🚀**
