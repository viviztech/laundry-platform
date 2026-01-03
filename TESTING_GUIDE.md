# LaundryConnect - Testing Guide

## Phase 4: Payment Integration Testing

This guide will help you test all the payment-related APIs that were implemented in Phase 4.

## Prerequisites

1. Activate virtual environment:
```bash
source venv/bin/activate
```

2. Run migrations (if not already done):
```bash
python manage.py migrate
```

3. Create a superuser (if not already done):
```bash
python manage.py createsuperuser
```

4. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints Overview

### Payment Endpoints
- `GET /api/payments/payments/` - List all payments
- `POST /api/payments/payments/` - Create a new payment
- `GET /api/payments/payments/{id}/` - Get payment details
- `POST /api/payments/payments/{id}/verify/` - Verify payment

### Wallet Endpoints
- `GET /api/payments/wallets/` - List wallets
- `GET /api/payments/wallets/{id}/` - Get wallet details
- `POST /api/payments/wallets/{id}/add_balance/` - Add balance to wallet
- `GET /api/payments/wallets/{id}/transactions/` - Get wallet transaction history

### Refund Endpoints
- `GET /api/payments/refunds/` - List refunds
- `POST /api/payments/refunds/` - Request a refund
- `GET /api/payments/refunds/{id}/` - Get refund details
- `POST /api/payments/refunds/{id}/process/` - Process refund (admin only)

### Payment Method Endpoints
- `GET /api/payments/payment-methods/` - List saved payment methods
- `POST /api/payments/payment-methods/` - Add a payment method
- `GET /api/payments/payment-methods/{id}/` - Get payment method details
- `POST /api/payments/payment-methods/{id}/set_default/` - Set as default
- `DELETE /api/payments/payment-methods/{id}/` - Delete payment method

## Testing with API Documentation

### Using Swagger UI
1. Navigate to: http://localhost:8000/api/docs/
2. Click "Authorize" and enter your JWT token
3. Test all payment endpoints interactively

### Using ReDoc
1. Navigate to: http://localhost:8000/api/redoc/
2. View comprehensive API documentation

## Manual Testing with cURL

### 1. Get Authentication Token

```bash
# Register/Login to get token
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# Save the access token for subsequent requests
export TOKEN="your-access-token-here"
```

### 2. Test Payment Methods

#### Add a UPI Payment Method
```bash
curl -X POST http://localhost:8000/api/payments/payment-methods/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "upi",
    "nickname": "My PhonePe",
    "upi_id": "user@phonepe",
    "is_default": true,
    "card_token": ""
  }'
```

#### Add a Card Payment Method
```bash
curl -X POST http://localhost:8000/api/payments/payment-methods/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "card",
    "nickname": "My Visa Card",
    "card_token": "tok_dummy_token",
    "card_last4": "4242",
    "card_brand": "Visa",
    "card_expiry_month": 12,
    "card_expiry_year": 2025,
    "is_default": false
  }'
```

#### List Payment Methods
```bash
curl -X GET http://localhost:8000/api/payments/payment-methods/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Payments

#### Create a Payment (requires an order first)
```bash
# First, create an order (see orders API)
# Then create payment with the order_id

curl -X POST http://localhost:8000/api/payments/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "your-order-uuid",
    "payment_method": "upi",
    "gateway": "razorpay"
  }'
```

#### Verify a Payment
```bash
curl -X POST http://localhost:8000/api/payments/payments/{payment-id}/verify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_payment_id": "pay_dummy123",
    "gateway_order_id": "order_dummy123",
    "gateway_signature": "signature_dummy"
  }'
```

#### List Payments
```bash
curl -X GET http://localhost:8000/api/payments/payments/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Test Wallet

#### Get My Wallet
```bash
curl -X GET http://localhost:8000/api/payments/wallets/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Add Balance to Wallet
```bash
curl -X POST http://localhost:8000/api/payments/wallets/{wallet-id}/add_balance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "500.00",
    "description": "Added via API"
  }'
```

#### Get Wallet Transaction History
```bash
curl -X GET http://localhost:8000/api/payments/wallets/{wallet-id}/transactions/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Test Refunds

#### Request a Refund
```bash
curl -X POST http://localhost:8000/api/payments/refunds/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "payment-uuid",
    "amount": "100.00",
    "reason": "service_issue",
    "description": "Service was not satisfactory"
  }'
```

#### Process a Refund (Admin Only)
```bash
curl -X POST http://localhost:8000/api/payments/refunds/{refund-id}/process/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "gateway_refund_id": "rfnd_dummy123"
  }'
```

#### List Refunds
```bash
curl -X GET http://localhost:8000/api/payments/refunds/ \
  -H "Authorization: Bearer $TOKEN"
```

## Testing with Django Admin

1. Navigate to: http://localhost:8000/admin/
2. Login with your superuser credentials
3. Access these models:
   - Payments > Payments
   - Payments > Wallets
   - Payments > Wallet Transactions
   - Payments > Refunds
   - Payments > Payment Methods

## Testing with Python Shell

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.payments.models import Payment, Wallet, PaymentMethod, Refund
from apps.orders.models import Order
from decimal import Decimal

# Create a test user
user = User.objects.create_user(
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User',
    phone='1234567890',
    user_type='customer'
)

# Create a wallet for the user
wallet = Wallet.objects.create(user=user)

# Add balance to wallet
wallet.add_balance(
    amount=Decimal('1000.00'),
    description='Initial balance'
)

# Check wallet balance
print(f"Wallet Balance: {wallet.balance}")

# Get transaction history
transactions = wallet.transactions.all()
for txn in transactions:
    print(f"{txn.transaction_id}: {txn.transaction_type} - {txn.amount}")

# Create a payment method
payment_method = PaymentMethod.objects.create(
    user=user,
    type='upi',
    nickname='Test UPI',
    upi_id='test@paytm',
    is_default=True
)

# List all payment methods
methods = PaymentMethod.objects.filter(user=user)
for method in methods:
    print(f"{method.type}: {method}")
```

## Verification Checklist

### ✅ Models
- [ ] Payment model creates with auto-generated payment_id
- [ ] Wallet model creates and balance operations work
- [ ] WalletTransaction auto-creates on balance changes
- [ ] Refund model creates with auto-generated refund_id
- [ ] PaymentMethod model saves correctly

### ✅ API Endpoints
- [ ] All payment endpoints return 200/201 on success
- [ ] Authentication is required for all endpoints
- [ ] Users can only see their own data
- [ ] Admins can see all data
- [ ] Proper error messages on validation failures

### ✅ Business Logic
- [ ] Only one default payment method per user
- [ ] Wallet balance updates correctly on add/deduct
- [ ] Transaction history is automatically created
- [ ] Refund amount cannot exceed payment amount
- [ ] Payment status updates when refunded

### ✅ Admin Interface
- [ ] All models are registered in admin
- [ ] Inline editing works for related models
- [ ] Filters and search work correctly
- [ ] Read-only fields are protected

## Common Test Scenarios

### Scenario 1: Complete Payment Flow
1. User creates an order
2. User initiates payment for the order
3. Payment gateway processes (simulated)
4. User verifies payment
5. Order status updates to paid

### Scenario 2: Wallet Operations
1. User adds balance to wallet
2. User views transaction history
3. User uses wallet balance for payment
4. Wallet balance decreases
5. Transaction history shows debit

### Scenario 3: Refund Flow
1. User requests refund for completed payment
2. Admin reviews refund request
3. Admin processes refund
4. Payment status updates to refunded
5. User receives refund

### Scenario 4: Payment Methods
1. User adds multiple payment methods
2. User sets one as default
3. User makes payment using saved method
4. User deletes old payment method

## Troubleshooting

### Issue: "DATABASES is improperly configured"
**Solution**: Ensure your `.env` file has correct database credentials

### Issue: "No module named 'apps.payments'"
**Solution**: Run `python manage.py check` to verify app is installed

### Issue: "Authentication credentials were not provided"
**Solution**: Include `Authorization: Bearer <token>` header in requests

### Issue: "Object does not exist"
**Solution**: Ensure you're using valid UUIDs from created objects

## Next Steps

After testing Phase 4:
1. Fix any bugs discovered during testing
2. Consider implementing Phase 5 (Notifications)
3. Add unit tests for payment functionality
4. Integrate actual payment gateway (Razorpay/Stripe)
5. Add payment webhooks for gateway callbacks

## Notes

- All IDs are UUIDs, not integers
- Payment gateway integration is stubbed (ready for actual implementation)
- Wallet system is fully functional
- Refund workflow requires admin approval
- All financial amounts use Decimal for precision
