# Partner Admin Panel Guide
**LaundryConnect Platform - Partner Launch Edition**

---

## 🎯 Overview

This guide is for the **partner-focused launch** of LaundryConnect. The admin panel provides comprehensive tools for managing partner businesses, orders, services, and customer interactions.

---

## 🔐 Access Information

### Admin Login
- **URL**: http://localhost:8000/admin/
- **Email**: `admin@laundryconnect.com`
- **Password**: `admin123`

### Partner Login (for testing partner view)
- **Email**: `cleanpro@business.com`
- **Password**: `partner123`

### Customer Login (for testing customer view)
- **Email**: `demo.customer@test.com`
- **Password**: `demo123`

---

## 📊 Priority Modules for Partner Launch

### **1. PARTNERS (Core Module)**
Location: Admin > Partners > Partners

**What you can manage:**
- ✅ Partner business profiles
- ✅ Verification status
- ✅ Service areas and coverage
- ✅ Availability schedules
- ✅ Performance metrics (ratings, completed orders)
- ✅ Commission rates
- ✅ Bank account details

**Key Actions:**
- Add new partner businesses
- Verify and activate partners
- View partner performance dashboard
- Manage service radius and capacity
- Update bank details for payouts

**Available Demo Partners:**
1. **CleanPro Laundry Services** (Indiranagar - Zone A)
2. **Sparkle Wash & Dry** (Koramangala - Zone B)
3. **Fresh & Clean Laundry** (HSR Layout - Zone C)

---

### **2. PARTNER AVAILABILITY**
Location: Admin > Partners > Partner Availability

**What you can manage:**
- ✅ Weekly schedules (Monday-Sunday)
- ✅ Operating hours per day
- ✅ Holiday management
- ✅ Temporary unavailability

**Features:**
- Set different hours for different days
- Mark partners as unavailable
- Manage public holidays
- Handle emergency closures

---

### **3. PARTNER SERVICE AREAS**
Location: Admin > Partners > Partner Service Areas

**What you can manage:**
- ✅ Pin code coverage
- ✅ Area-specific delivery charges
- ✅ Service area activation/deactivation

**Use Case:**
- Define which pin codes each partner serves
- Set extra delivery charges for distant areas
- Quickly enable/disable service in specific areas

---

### **4. ORDERS (Critical)**
Location: Admin > Orders > Orders

**What you can manage:**
- ✅ All order lifecycle stages
- ✅ Order assignment to partners
- ✅ Status updates (pending → delivered)
- ✅ Order items and pricing
- ✅ Special instructions

**Order Statuses:**
1. `pending` - New order, awaiting confirmation
2. `confirmed` - Partner confirmed, ready for pickup
3. `picked_up` - Items collected from customer
4. `in_progress` - Currently being processed
5. `ready` - Cleaning complete, ready for delivery
6. `out_for_delivery` - On the way to customer
7. `delivered` - Successfully delivered
8. `completed` - Order closed
9. `cancelled` - Order cancelled

**Key Features:**
- Bulk order status updates
- Filter by status, partner, customer
- View order timeline
- Generate invoices

---

### **5. SERVICES & PRICING**
Location: Admin > Services

**What you can manage:**
- ✅ Service categories (Wash & Iron, Dry Cleaning, etc.)
- ✅ Garment types (Shirt, Trouser, Dress, etc.)
- ✅ Services (combinations of category + garment)
- ✅ Zone-based pricing (A, B, C)
- ✅ Service pricing with discounts

**Current Service Categories:**
1. **Wash & Iron** 🧺 - Everyday garments
2. **Dry Cleaning** 👔 - Delicate fabrics
3. **Iron Only** 🔥 - Pre-washed clothes
4. **Wash Only** 💧 - No ironing
5. **Premium Care** ✨ - Designer garments
6. **Shoe Cleaning** 👟 - Footwear care

**Pricing Zones:**
- **Zone A** (Premium): 1.2x multiplier - Areas like Indiranagar, Whitefield
- **Zone B** (Standard): 1.0x multiplier - HSR, Koramangala, BTM
- **Zone C** (Economy): 0.9x multiplier - Jayanagar, Electronic City

---

### **6. PAYMENTS**
Location: Admin > Payments

**What you can manage:**
- ✅ Payment records for all orders
- ✅ Wallet balances
- ✅ Wallet transactions
- ✅ Refunds
- ✅ Payment methods

**Payment Methods:**
- Online (Razorpay, Paytm, PhonePe)
- Cash on Delivery (COD)
- Wallet

**Features:**
- Track payment status (pending/completed/failed)
- Process refunds
- Manage customer wallets
- View transaction history

---

### **7. CHAT & COMMUNICATION**
Location: Admin > Chat

**What you can manage:**
- ✅ Chat rooms between customers and partners
- ✅ Message history
- ✅ Active/inactive conversations

**Use Cases:**
- Customer support for order issues
- Partner communication with customers
- Resolve disputes
- Track conversation history

---

### **8. NOTIFICATIONS**
Location: Admin > Notifications

**What you can manage:**
- ✅ User notification preferences
- ✅ Sent notifications (Email, Push, SMS)
- ✅ Notification templates

**Types:**
- Order updates (status changes)
- Payment confirmations
- Delivery notifications
- Marketing messages

---

### **9. USERS & ACCOUNTS**
Location: Admin > Accounts

**What you can manage:**
- ✅ User accounts (Customers, Partners, Admin)
- ✅ User profiles
- ✅ Customer addresses
- ✅ User verification status

**User Types:**
- **Customer** - End users placing orders
- **Partner** - Laundry service providers
- **Admin** - Platform administrators

---

### **10. ANALYTICS (Optional)**
Location: Admin > Analytics

**What you can view:**
- ✅ Partner performance metrics
- ✅ Order statistics
- ✅ Revenue tracking
- ✅ Customer behavior

---

## 🚀 Quick Start Workflow for Partner Launch

### **Step 1: Add a New Partner**
1. Go to **Admin > Partners > Partners**
2. Click "Add Partner"
3. Fill in:
   - User account (email, phone)
   - Business details
   - Contact information
   - Address and location
   - Pricing zone
   - Service radius
   - Daily capacity
4. Upload documents (business license, tax certificate)
5. Save

### **Step 2: Set Partner Availability**
1. Go to **Admin > Partners > Partner Availability**
2. Create schedules for each day
3. Set operating hours (e.g., 9 AM - 9 PM)
4. Mark any holidays

### **Step 3: Define Service Areas**
1. Go to **Admin > Partners > Partner Service Areas**
2. Add pin codes the partner will serve
3. Set extra delivery charges if needed
4. Activate the service area

### **Step 4: Verify and Activate Partner**
1. Return to partner profile
2. Set status to "Active"
3. Mark as "Verified"
4. Partner is now live!

### **Step 5: Monitor Orders**
1. Go to **Admin > Orders > Orders**
2. View incoming orders
3. Assign to appropriate partners
4. Track status updates
5. Handle any issues

---

## 📱 Mobile App Integration

The mobile app connects to these admin panel features:

### **Partner App Features:**
- View assigned orders
- Update order status
- Manage availability
- Chat with customers
- View earnings

### **Customer App Features:**
- Browse services
- Place orders
- Track orders in real-time
- Chat with partners
- Manage addresses
- Wallet topup

---

## 🔧 Admin Panel Features

### **Dashboard**
- **Orders Today/Week/Month** - Quick metrics
- **Revenue Statistics** - Daily/weekly/monthly
- **Active Partners Count** - Verified and active
- **Pending Orders** - Requiring attention

### **Filtering & Search**
- Filter orders by status, partner, date
- Search partners by name, location, zone
- Search customers by email, phone
- Filter services by category

### **Bulk Actions**
- Update multiple order statuses
- Export data to CSV
- Send bulk notifications

### **Reports**
- Partner performance reports
- Revenue reports
- Order completion rates
- Customer satisfaction metrics

---

## 🎨 UI Customization (Django Unfold)

The admin panel uses **Django Unfold** for a modern, beautiful interface:
- Dark/Light theme toggle
- Mobile-responsive design
- Clean, intuitive navigation
- Advanced filtering
- Quick actions

---

## ⚠️ Important Notes for Partner Launch

### **Before Going Live:**
1. ✅ Verify all partner details are correct
2. ✅ Ensure pricing is set for all zones
3. ✅ Test order flow end-to-end
4. ✅ Configure payment gateways
5. ✅ Set up notification templates
6. ✅ Train partners on mobile app
7. ✅ Prepare customer support process

### **Security Checklist:**
- [ ] Change all default passwords
- [ ] Enable 2FA for admin accounts
- [ ] Review and set proper user permissions
- [ ] Configure HTTPS for production
- [ ] Set up regular database backups
- [ ] Configure rate limiting
- [ ] Review Django security settings

### **Performance Tips:**
- Use database indexing for large datasets
- Enable caching for frequently accessed data
- Monitor server resources
- Set up CDN for media files
- Use async tasks for heavy operations

---

## 📞 Support & Troubleshooting

### **Common Issues:**

**Issue:** Partner not receiving orders
- ✅ Check if partner status is "Active"
- ✅ Verify service areas are configured
- ✅ Confirm availability schedule is set
- ✅ Check daily capacity not exceeded

**Issue:** Pricing showing incorrectly
- ✅ Verify zone assignment for partner
- ✅ Check ServicePricing for that zone
- ✅ Ensure pricing is active

**Issue:** Customer can't place order
- ✅ Check if address is in covered pin code
- ✅ Verify services are active
- ✅ Check if any partner serves that area

---

## 📊 Data Models Reference

### **Key Relationships:**
```
Partner → Orders (assigned_orders)
Partner → ServiceAreas (service_areas)
Partner → Availability (availability)
Order → OrderItems (items)
Order → Payment (payment)
Order → ChatRoom (chat)
Service → ServicePricing (pricing)
User → Wallet (wallet)
User → Addresses (addresses)
```

---

## 🎯 Next Steps After Launch

1. **Monitor Performance**
   - Track order completion rates
   - Monitor partner ratings
   - Review customer feedback

2. **Optimize Operations**
   - Adjust pricing based on demand
   - Add more service areas
   - Recruit more partners in busy zones

3. **Enhance Features**
   - Add loyalty programs
   - Implement referral system
   - Introduce subscription plans

4. **Scale**
   - Expand to new cities
   - Add more service categories
   - Partner with corporate clients

---

## 📖 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/
- **ReDoc**: http://localhost:8000/api/redoc/

---

**Last Updated**: January 12, 2026
**Version**: 1.0.0 - Partner Launch Edition

---

## 🎉 Ready to Launch!

Your admin panel is fully configured and ready for the partner-focused launch. All essential modules are in place to manage:
- ✅ Partner onboarding and management
- ✅ Order processing and tracking
- ✅ Service catalog and pricing
- ✅ Customer relationships
- ✅ Payments and settlements
- ✅ Real-time communication

**Access your admin panel**: http://localhost:8000/admin/

Good luck with your launch! 🚀
