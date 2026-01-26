# SMS Integration Guide - LaundryConnect

**Phase 7 Feature**: SMS Notifications via Twilio
**Status**: ✅ Implemented
**Date**: 2026-01-03

---

## Overview

LaundryConnect now supports SMS notifications for critical order and payment events using Twilio. Users can receive instant SMS updates about their orders, payments, and account activities.

### Key Features

- ✅ **Automated SMS Notifications**: 21+ notification types with SMS templates
- ✅ **User Preferences**: Per-user SMS opt-in/opt-out controls
- ✅ **Multi-channel**: Email + SMS + WebSocket + Push (in progress)
- ✅ **Async Processing**: SMS sent via Celery for performance
- ✅ **Delivery Tracking**: Message SID and status stored in notification metadata
- ✅ **Error Handling**: Retry logic for temporary failures
- ✅ **Testing Tools**: Management command for testing SMS delivery

---

## Prerequisites

### 1. Twilio Account Setup

1. **Sign up** at [https://www.twilio.com/](https://www.twilio.com/)
2. **Get a phone number**:
   - Navigate to Phone Numbers → Buy a Number
   - Choose a number with SMS capabilities
   - For India: Get an Indian phone number (+91...)
3. **Get credentials**:
   - Account SID: Found on your Twilio Console Dashboard
   - Auth Token: Found on your Twilio Console Dashboard (click "Show" to reveal)

### 2. Cost Considerations

- **Free Trial**: $15 credit, can send ~500 SMS
- **Production Pricing** (India):
  - Outbound SMS: ~₹0.70 - ₹1.50 per message
  - Inbound SMS: Free
- **Phone Number**: ~₹850/month for Indian number

### 3. India SMS Regulations (DLT)

For production SMS in India, you need:
1. **DLT Registration**: Register with telecom operators
2. **Sender ID Approval**: Get your brand name approved
3. **Template Approval**: Submit and get SMS templates approved
4. **Entity ID**: Unique identifier from DLT portal

**Note**: For testing/development, Twilio trial accounts work without DLT.

---

## Installation & Configuration

### Step 1: Install Dependencies

```bash
# Already included in requirements/base.txt
pip install twilio==8.10.0
```

### Step 2: Add Environment Variables

Create/update your `.env` file:

```bash
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+919876543210  # Your Twilio phone number (E.164 format)

# Optional: Status callback URL for delivery reports
TWILIO_STATUS_CALLBACK_URL=https://yourdomain.com/api/sms/status-callback/
```

**E.164 Format**: Phone numbers must include `+` and country code
- India: `+919876543210`
- US: `+14155551234`

### Step 3: Verify Configuration

```bash
# Activate virtual environment
source venv/bin/activate

# Check if SMS is configured
python manage.py test_sms --check-config
```

Expected output:
```
============================================================
SMS Configuration Check
============================================================
✓ SMS service is enabled and configured
  Account SID: ACxxxxxxxx...
  From Number: +919876543210
============================================================
```

---

## SMS Architecture

### Flow Diagram

```
Django Signal (Order/Payment Created/Updated)
    ↓
create_notification()
    ↓
Notification.post_save signal
    ↓
broadcast_notification_created()
    ├── send_notification_email.delay() [Celery]
    ├── send_notification_sms.delay() [Celery] ← NEW
    └── WebSocket broadcast
        ↓
Celery Worker picks up task
    ↓
send_notification_sms()
    ├── Check if SMS enabled
    ├── Check if user has phone number
    ├── Check user preferences
    ├── Get SMS template
    ├── Render template with context
    └── Send via Twilio API
        ↓
Store result in notification.metadata
```

### Files Added/Modified

| File | Purpose |
|------|---------|
| [apps/notifications/sms.py](apps/notifications/sms.py) | SMS service with Twilio integration |
| [apps/notifications/tasks.py](apps/notifications/tasks.py) | Added `send_notification_sms` Celery task |
| [apps/notifications/signals.py](apps/notifications/signals.py) | Added SMS sending to notification signal |
| [apps/notifications/management/commands/test_sms.py](apps/notifications/management/commands/test_sms.py) | Testing command |
| [config/settings/development.py](config/settings/development.py) | Twilio configuration |

---

## SMS Templates

### Template Structure

Each notification type has an SMS template in the `NotificationTemplate` model:

```python
sms_template = "LaundryConnect: Order #{{ order.order_number }} confirmed! Pickup on {{ order.pickup_date }}."
```

### SMS Template Guidelines

1. **Length**: Keep under 160 characters for single SMS (longer messages are split)
2. **Brand Name**: Start with "LaundryConnect:" for brand recognition
3. **Key Info**: Include order number, amount, or critical data
4. **Call to Action**: Add link or next step when relevant
5. **Personalization**: Use `{{ first_name }}`, `{{ order.order_number }}`, etc.

### Example Templates

#### Order Confirmed
```
LaundryConnect: Order #{{ order.order_number }} confirmed! Pickup scheduled for {{ order.pickup_date }}. Thank you!
```

#### Order Out for Delivery
```
LaundryConnect: Your order #{{ order.order_number }} is out for delivery! It will reach you shortly. Track live at laundryconnect.com
```

#### Payment Completed
```
LaundryConnect: Payment of ₹{{ payment.amount }} successful! Transaction ID: {{ payment.transaction_id }}. Thank you!
```

---

## User Preferences

### SMS Opt-in/Opt-out

Users can control SMS notifications via `NotificationPreference` model:

```python
class NotificationPreference(models.Model):
    # SMS preferences
    order_updates_sms = models.BooleanField(default=False)
    payment_updates_sms = models.BooleanField(default=False)
```

**Default**: SMS is **disabled by default** (opt-in required)

### API Endpoint to Update Preferences

```bash
# Update SMS preferences
curl -X PATCH http://localhost:8000/api/notifications/preferences/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_updates_sms": true,
    "payment_updates_sms": true
  }'
```

---

## Testing SMS

### Method 1: Management Command

#### Check Configuration
```bash
python manage.py test_sms --check-config
```

#### Send Test SMS to Any Number
```bash
python manage.py test_sms --phone "+919876543210" --message "Hello from LaundryConnect!"
```

#### Send Test Notification SMS to User
```bash
python manage.py test_sms --user-email "user@example.com"
```

### Method 2: Django Shell

```python
python manage.py shell

from apps.notifications.sms import sms_service
from django.contrib.auth import get_user_model

User = get_user_model()

# Test basic SMS sending
result = sms_service.send_sms(
    to_number="+919876543210",
    message="Test SMS from LaundryConnect!",
    notification_id="TEST"
)

print(result)
# Output: {'success': True, 'message_sid': 'SMxxxxx', 'status': 'queued', ...}

# Test notification SMS
user = User.objects.get(email="user@example.com")
context = {'user': user, 'order': {'order_number': 'ORD001'}}

result = sms_service.send_notification_sms(
    user=user,
    notification_type='order_confirmed',
    context=context
)

print(result)
```

### Method 3: Create Notification Programmatically

```python
from apps.notifications.utils import create_notification
from apps.accounts.models import User

user = User.objects.first()

# This will trigger email, SMS, and WebSocket notifications
notification = create_notification(
    user=user,
    notification_type='order_confirmed',
    order=order_instance  # Pass your order object
)
```

---

## SMS Delivery Tracking

### Metadata Storage

SMS delivery information is stored in `Notification.metadata`:

```python
notification = Notification.objects.get(notification_id='NOTIF123')

print(notification.metadata)
# Output:
{
    "sms": {
        "sent": true,
        "message_sid": "SM1234567890abcdef",
        "sent_at": "2026-01-03T10:30:00Z",
        "status": "sent",
        "to": "+919876543210"
    }
}
```

### Twilio Message Statuses

- `queued`: Message queued for sending
- `sending`: Message is being sent
- `sent`: Message sent to carrier
- `delivered`: Message delivered to recipient (requires status callbacks)
- `undelivered`: Message could not be delivered
- `failed`: Message sending failed

### Check Message Status

```python
from apps.notifications.sms import sms_service

# Get status by message SID
status = sms_service.get_message_status('SM1234567890abcdef')

print(status)
# Output: {'status': 'delivered', 'to': '+919876543210', 'price': '0.0070', ...}
```

---

## Error Handling

### Common Errors

#### 1. SMS Service Not Configured
```
Error: SMS service not configured
```
**Solution**: Add Twilio credentials to `.env` file

#### 2. Invalid Phone Number
```
Error: Invalid phone number format. Must start with + and country code.
```
**Solution**: Use E.164 format: `+919876543210`

#### 3. User Has No Phone Number
```
Info: User user@example.com has no phone number. Skipping SMS.
```
**Solution**: Users must have `phone` field populated in database

#### 4. User Disabled SMS
```
Info: User has disabled SMS notifications
```
**Solution**: User needs to enable SMS in notification preferences

#### 5. Twilio Authentication Error
```
Error: Twilio error: Authenticate
```
**Solution**: Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are correct

### Retry Logic

- **Automatic Retries**: Failed SMS are retried up to 3 times
- **Retry Delay**: 5 minutes (300 seconds) between retries
- **No Retry Cases**:
  - User has disabled SMS (`disabled_by_user`)
  - User has no phone number
  - Invalid phone number format

---

## SMS Notification Types

### Critical (High Priority)

These are sent immediately via SMS when user has opted in:

1. **order_confirmed** - Order confirmed and scheduled
2. **order_out_for_delivery** - Order is being delivered
3. **order_delivered** - Order delivered successfully
4. **payment_completed** - Payment successful
5. **refund_completed** - Refund processed

### Regular (Medium Priority)

Sent based on user preferences:

6. **order_created** - New order placed
7. **order_picked_up** - Laundry picked up
8. **order_ready** - Order ready for delivery
9. **payment_initiated** - Payment processing
10. **refund_requested** - Refund request received

### Account & Partner

11. **welcome** - New user registration (includes promo code)
12. **account_verified** - Account verified successfully
13. **partner_approved** - Partner account approved
14. **new_order_assigned** - New order assigned to partner

---

## Production Deployment

### 1. Environment Configuration

```bash
# Production .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx  # Production Account SID
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx    # Production Auth Token
TWILIO_PHONE_NUMBER=+919876543210  # Production phone number
TWILIO_STATUS_CALLBACK_URL=https://api.laundryconnect.com/sms/callback/
```

### 2. DLT Registration (India Only)

For production SMS in India:

1. Register on DLT portal: https://www.vilpower.in/
2. Get Entity ID
3. Register Sender ID (e.g., "LNDCON")
4. Submit and approve all SMS templates
5. Configure in Twilio:
   - Settings → Compliance → India DLT
   - Add Entity ID and Sender ID

### 3. Status Callbacks

To track delivery status, set up callback webhook:

```python
# apps/notifications/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])  # Twilio webhook
def sms_status_callback(request):
    """
    Webhook to receive SMS delivery status from Twilio.
    """
    message_sid = request.data.get('MessageSid')
    message_status = request.data.get('MessageStatus')

    # Update notification metadata
    notification = Notification.objects.filter(
        metadata__sms__message_sid=message_sid
    ).first()

    if notification:
        notification.metadata['sms']['status'] = message_status
        notification.metadata['sms']['updated_at'] = timezone.now().isoformat()
        notification.save(update_fields=['metadata'])

    return Response({'status': 'ok'})
```

### 4. Monitor SMS Usage

```python
# Get SMS stats
from apps.notifications.models import Notification

# Total SMS sent today
from django.utils import timezone
from datetime import timedelta

today = timezone.now().date()
sms_sent_today = Notification.objects.filter(
    metadata__sms__sent=True,
    created_at__date=today
).count()

print(f"SMS sent today: {sms_sent_today}")
```

---

## Best Practices

### 1. SMS Hygiene

- ✅ Always validate phone numbers before sending
- ✅ Allow users to opt-out easily
- ✅ Send only critical/important notifications
- ✅ Respect user preferences
- ✅ Monitor delivery rates

### 2. Cost Optimization

- ✅ Make SMS opt-in (not opt-out) - **Default: disabled**
- ✅ Only send high-priority notifications via SMS
- ✅ Use email for detailed information, SMS for alerts
- ✅ Batch non-urgent notifications
- ✅ Set daily/monthly SMS limits per user

### 3. Security

- ✅ Never include sensitive data (passwords, full card numbers)
- ✅ Use HTTPS for callback URLs
- ✅ Validate Twilio webhook signatures
- ✅ Store credentials in environment variables
- ✅ Rotate Auth Tokens periodically

### 4. User Experience

- ✅ Keep messages concise and actionable
- ✅ Include brand name ("LaundryConnect:")
- ✅ Add tracking links for orders
- ✅ Provide opt-out instructions
- ✅ Send at appropriate times (not late night)

---

## Troubleshooting

### SMS Not Being Sent

**Check 1**: Is SMS service enabled?
```bash
python manage.py test_sms --check-config
```

**Check 2**: Does user have phone number?
```python
user = User.objects.get(email="user@example.com")
print(user.phone)  # Should print phone number
```

**Check 3**: Has user opted in?
```python
prefs = user.notification_preferences
print(prefs.order_updates_sms)  # Should be True
```

**Check 4**: Is Celery running?
```bash
# Check Celery worker logs
celery -A config worker -l info
```

**Check 5**: Check Twilio logs
- Go to Twilio Console → Monitor → Logs → Messaging
- Look for errors or failed messages

### Phone Number Format Issues

```python
# Wrong formats:
"9876543210"          # ✗ Missing country code
"919876543210"        # ✗ Missing +
"+91 9876543210"      # ✗ Has space
"+91-9876-543210"     # ✗ Has hyphens

# Correct format:
"+919876543210"       # ✓ E.164 format
```

### Template Not Found

```bash
# Load templates
python manage.py load_notification_templates

# Verify templates
python manage.py shell
>>> from apps.notifications.models import NotificationTemplate
>>> NotificationTemplate.objects.filter(type='order_confirmed').exists()
True
```

---

## Future Enhancements

- [ ] **Two-way SMS**: Reply to SMS for order confirmation
- [ ] **Smart Routing**: Route to cheapest SMS provider
- [ ] **Local Language**: SMS in Hindi, Tamil, etc.
- [ ] **Rich SMS**: MMS with images (order photos)
- [ ] **SMS Campaigns**: Bulk promotional SMS
- [ ] **SMS Analytics**: Dashboard with delivery rates
- [ ] **A/B Testing**: Test different SMS templates
- [ ] **Time Zone Aware**: Send SMS based on user's local time

---

## Support

### Documentation
- Twilio Docs: https://www.twilio.com/docs/sms
- Twilio Python SDK: https://www.twilio.com/docs/libraries/python
- India DLT: https://www.trai.gov.in/

### Contact
- **Technical Issues**: Create issue on GitHub
- **Twilio Support**: https://support.twilio.com/

---

**SMS Integration**: ✅ **Complete**
**Date**: 2026-01-03
**Next Phase**: Push Notifications (Web Push API)

---

Generated with [Claude Code](https://claude.com/claude-code)
