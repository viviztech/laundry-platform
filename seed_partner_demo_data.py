"""
Enhanced Partner-Focused Demo Data Seed Script for LaundryConnect
This script creates comprehensive demo data optimized for partner launch
Run with: python manage.py shell < seed_partner_demo_data.py
"""
from django.utils.text import slugify
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta, time, date

# Import all necessary models
from apps.accounts.models import User, UserProfile, Address
from apps.services.models import ServiceCategory, GarmentType, Service, PricingZone, ServicePricing
from apps.partners.models import Partner, PartnerAvailability, PartnerServiceArea, PartnerHoliday
from apps.orders.models import Order, OrderItem
from apps.payments.models import Wallet, Payment, WalletTransaction
from apps.chat.models import ChatRoom, ChatMessage
from apps.notifications.models import Notification, NotificationPreference

print("=" * 80)
print("SEEDING LAUNDRYCONNECT PARTNER-FOCUSED DEMO DATA")
print("=" * 80)

# =============================================================================
# 1. CREATE USER GROUPS WITH PERMISSIONS
# =============================================================================
print("\n[1/12] Creating user groups and permissions...")

groups_config = {
    'Customer': {
        'description': 'Regular customers who place orders',
        'permissions': [
            ('orders', 'order', ['add', 'view', 'change']),
            ('accounts', 'address', ['add', 'view', 'change', 'delete']),
            ('payments', 'wallet', ['view']),
            ('chat', 'chatroom', ['view']),
            ('chat', 'chatmessage', ['add', 'view']),
        ]
    },
    'Partner': {
        'description': 'Laundry service partners',
        'permissions': [
            ('partners', 'partner', ['view', 'change']),
            ('orders', 'order', ['view', 'change']),
            ('partners', 'partneravailability', ['add', 'view', 'change', 'delete']),
            ('partners', 'partnerservicearea', ['add', 'view', 'change', 'delete']),
            ('partners', 'partnerholiday', ['add', 'view', 'change', 'delete']),
            ('chat', 'chatroom', ['view']),
            ('chat', 'chatmessage', ['add', 'view']),
            ('payments', 'payment', ['view']),
        ]
    },
    'Admin': {
        'description': 'Platform administrators',
        'permissions': [
            ('orders', 'order', ['add', 'view', 'change', 'delete']),
            ('accounts', 'user', ['add', 'view', 'change', 'delete']),
            ('partners', 'partner', ['add', 'view', 'change', 'delete']),
            ('services', 'service', ['add', 'view', 'change', 'delete']),
            ('services', 'servicecategory', ['add', 'view', 'change', 'delete']),
            ('services', 'pricingzone', ['add', 'view', 'change', 'delete']),
            ('payments', 'wallet', ['add', 'view', 'change', 'delete']),
            ('payments', 'payment', ['add', 'view', 'change', 'delete']),
        ]
    },
}

created_groups = {}
for group_name, config in groups_config.items():
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        for app_label, model_name, perm_types in config['permissions']:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                for perm_type in perm_types:
                    codename = f'{perm_type}_{model_name}'
                    try:
                        permission = Permission.objects.get(codename=codename, content_type=content_type)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass
            except ContentType.DoesNotExist:
                pass
    created_groups[group_name] = group
    print(f"  ✓ {group_name}: {config['description']}")

print(f"  Total: {len(created_groups)} groups created")

# =============================================================================
# 2. CREATE PRICING ZONES
# =============================================================================
print("\n[2/12] Creating pricing zones...")
zone_a, _ = PricingZone.objects.get_or_create(
    zone='A',
    defaults={
        'name': 'Zone A - Premium',
        'description': 'Premium residential areas (Indiranagar, Koramangala, Whitefield)',
        'multiplier': Decimal('1.2')
    }
)
zone_b, _ = PricingZone.objects.get_or_create(
    zone='B',
    defaults={
        'name': 'Zone B - Standard',
        'description': 'Standard residential areas (HSR Layout, BTM, Marathahalli)',
        'multiplier': Decimal('1.0')
    }
)
zone_c, _ = PricingZone.objects.get_or_create(
    zone='C',
    defaults={
        'name': 'Zone C - Economy',
        'description': 'Economy areas with competitive pricing (Yeshwanthpur, Jayanagar)',
        'multiplier': Decimal('0.9')
    }
)
zones = [zone_a, zone_b, zone_c]
print(f"  ✓ Created 3 pricing zones: {', '.join([z.name for z in zones])}")

# =============================================================================
# 3. CREATE SERVICE CATEGORIES
# =============================================================================
print("\n[3/12] Creating service categories...")
categories_data = [
    ('Wash & Iron', 'wash-iron', 'Complete washing and ironing service for everyday garments', '🧺'),
    ('Dry Cleaning', 'dry-cleaning', 'Professional dry cleaning for delicate and premium fabrics', '👔'),
    ('Iron Only', 'iron-only', 'Quick ironing service for already clean clothes', '🔥'),
    ('Wash Only', 'wash-only', 'Washing service without ironing', '💧'),
    ('Premium Care', 'premium-care', 'Special care for designer and premium garments', '✨'),
    ('Shoe Cleaning', 'shoe-cleaning', 'Professional shoe and sneaker cleaning service', '👟'),
]

categories = {}
for name, slug, desc, icon in categories_data:
    cat, created = ServiceCategory.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'description': desc, 'is_active': True}
    )
    categories[slug] = cat
    if created:
        print(f"  ✓ {icon} {name}")

print(f"  Total: {len(categories)} categories")

# =============================================================================
# 4. CREATE GARMENT TYPES & SERVICES WITH PRICING
# =============================================================================
print("\n[4/12] Creating garment types and services...")

services_data = [
    # Wash & Iron
    ('Shirt', 'wash-iron', 30, 25),
    ('T-Shirt', 'wash-iron', 25, 20),
    ('Jeans', 'wash-iron', 50, 40),
    ('Trousers', 'wash-iron', 40, 35),
    ('Saree', 'wash-iron', 80, 70),
    ('Kurta', 'wash-iron', 45, 40),
    ('Salwar Kameez', 'wash-iron', 60, 50),
    ('Bedsheet', 'wash-iron', 70, 60),

    # Dry Cleaning
    ('Suit 2-piece', 'dry-cleaning', 300, 280),
    ('Suit 3-piece', 'dry-cleaning', 400, 380),
    ('Blazer', 'dry-cleaning', 200, 180),
    ('Dress', 'dry-cleaning', 150, 130),
    ('Coat', 'dry-cleaning', 250, 230),
    ('Sherwani', 'dry-cleaning', 500, 450),

    # Iron Only
    ('Shirt (Iron)', 'iron-only', 15, 12),
    ('Trousers (Iron)', 'iron-only', 20, 18),
    ('Saree (Iron)', 'iron-only', 40, 35),

    # Premium Care
    ('Wedding Attire', 'premium-care', 800, 750),
    ('Designer Dress', 'premium-care', 600, 550),
    ('Leather Jacket', 'premium-care', 700, 650),

    # Shoe Cleaning
    ('Sneakers', 'shoe-cleaning', 150, 120),
    ('Formal Shoes', 'shoe-cleaning', 120, 100),
    ('Boots', 'shoe-cleaning', 180, 150),
]

services_created = 0
for garment_name, cat_slug, base_price, discount_price in services_data:
    category = categories[cat_slug]

    # Create garment type
    garment, _ = GarmentType.objects.get_or_create(
        name=garment_name,
        defaults={'category': category, 'slug': slugify(garment_name)}
    )

    # Create service
    service, created = Service.objects.get_or_create(
        category=category,
        garment=garment,
        turnaround_time='standard',
        defaults={
            'name': f"{category.name} - {garment_name}",
            'description': f'Professional {category.name.lower()} service for {garment_name.lower()}',
            'is_active': True,
        }
    )

    if created:
        # Create pricing for all zones
        for zone in zones:
            zone_base = Decimal(str(base_price)) * zone.multiplier
            zone_discount = Decimal(str(discount_price)) * zone.multiplier

            ServicePricing.objects.get_or_create(
                service=service,
                zone=zone,
                defaults={
                    'base_price': zone_base.quantize(Decimal('0.01')),
                    'discount_price': zone_discount.quantize(Decimal('0.01')),
                }
            )
        services_created += 1

print(f"  ✓ Created {services_created} services with zone-based pricing")

# =============================================================================
# 5. CREATE DEMO USERS (Customers)
# =============================================================================
print("\n[5/12] Creating customer accounts...")

customers_data = [
    ('demo.customer@test.com', 'Demo', 'Customer', '+919000000001'),
    ('rajesh.kumar@gmail.com', 'Rajesh', 'Kumar', '+919000000002'),
    ('priya.sharma@gmail.com', 'Priya', 'Sharma', '+919000000003'),
    ('amit.patel@gmail.com', 'Amit', 'Patel', '+919000000004'),
    ('sneha.reddy@gmail.com', 'Sneha', 'Reddy', '+919000000005'),
    ('vikram.singh@gmail.com', 'Vikram', 'Singh', '+919000000006'),
    ('anjali.mehta@gmail.com', 'Anjali', 'Mehta', '+919000000007'),
    ('arjun.nair@gmail.com', 'Arjun', 'Nair', '+919000000008'),
]

customers = []
customer_group = created_groups['Customer']

for email, first_name, last_name, phone in customers_data:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'user_type': 'customer',
            'is_active': True,
            'is_verified': True,
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        user.groups.add(customer_group)

        # Create user profile
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'date_of_birth': date(1990, 1, 1) + timedelta(days=random.randint(0, 10000)),
                'gender': random.choice(['male', 'female']),
                'preferred_language': 'en',
            }
        )

        # Create wallet
        Wallet.objects.get_or_create(
            user=user,
            defaults={'balance': Decimal(str(random.randint(0, 500)))}
        )

        # Create notification preferences
        NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'order_updates_email': True,
                'order_updates_push': True,
                'payment_updates_email': True,
                'payment_updates_push': True,
                'marketing_emails': random.choice([True, False]),
            }
        )

    customers.append(user)

print(f"  ✓ Created {len(customers)} customer accounts")

# =============================================================================
# 6. CREATE CUSTOMER ADDRESSES
# =============================================================================
print("\n[6/12] Creating customer addresses...")

bangalore_areas = [
    ('Indiranagar', '560038', 12.9716, 77.6412, zone_a),
    ('Koramangala', '560095', 12.9352, 77.6245, zone_b),
    ('HSR Layout', '560102', 12.9121, 77.6446, zone_b),
    ('Whitefield', '560066', 12.9698, 77.7499, zone_a),
    ('BTM Layout', '560076', 12.9165, 77.6101, zone_b),
    ('Marathahalli', '560037', 12.9591, 77.6974, zone_b),
    ('Jayanagar', '560041', 12.9250, 77.5838, zone_c),
    ('Electronic City', '560100', 12.8456, 77.6603, zone_c),
]

addresses_created = 0
for customer in customers:
    # Create 1-2 addresses per customer
    num_addresses = random.randint(1, 2)
    for i in range(num_addresses):
        area, pincode, lat, lng, zone = random.choice(bangalore_areas)

        Address.objects.get_or_create(
            user=customer,
            address_type='home' if i == 0 else random.choice(['home', 'work', 'other']),
            address_line1=f"{random.randint(100, 999)}, {random.choice(['MG Road', 'Main Street', 'Cross Road', 'Park Avenue'])}",
            defaults={
                'address_line2': area,
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': pincode,
                'latitude': Decimal(str(lat)),
                'longitude': Decimal(str(lng)),
                'is_default': i == 0,
            }
        )
        addresses_created += 1

print(f"  ✓ Created {addresses_created} addresses across Bangalore areas")

# =============================================================================
# 7. CREATE PARTNER BUSINESSES
# =============================================================================
print("\n[7/12] Creating partner businesses...")

partners_data = [
    {
        'email': 'cleanpro@business.com',
        'business_name': 'CleanPro Laundry Services',
        'business_type': 'company',
        'contact_person': 'Ramesh Kumar',
        'contact_phone': '+919100000001',
        'area': 'Indiranagar',
        'pincode': '560038',
        'lat': 12.9716,
        'lng': 77.6412,
        'zone': zone_a,
        'capacity': 100,
    },
    {
        'email': 'sparklewash@business.com',
        'business_name': 'Sparkle Wash & Dry',
        'business_type': 'company',
        'contact_person': 'Priya Menon',
        'contact_phone': '+919100000002',
        'area': 'Koramangala',
        'pincode': '560095',
        'lat': 12.9352,
        'lng': 77.6245,
        'zone': zone_b,
        'capacity': 80,
    },
    {
        'email': 'freshclean@business.com',
        'business_name': 'Fresh & Clean Laundry',
        'business_type': 'individual',
        'contact_person': 'Suresh Reddy',
        'contact_phone': '+919100000003',
        'area': 'HSR Layout',
        'pincode': '560102',
        'lat': 12.9121,
        'lng': 77.6446,
        'zone': zone_c,
        'capacity': 60,
    },
    {
        'email': 'premium.care@business.com',
        'business_name': 'Premium Care Dry Cleaners',
        'business_type': 'company',
        'contact_person': 'Kavita Shah',
        'contact_phone': '+919100000004',
        'area': 'Whitefield',
        'pincode': '560066',
        'lat': 12.9698,
        'lng': 77.7499,
        'zone': zone_a,
        'capacity': 120,
    },
    {
        'email': 'express.laundry@business.com',
        'business_name': 'Express Laundry Services',
        'business_type': 'franchise',
        'contact_person': 'Arun Patel',
        'contact_phone': '+919100000005',
        'area': 'BTM Layout',
        'pincode': '560076',
        'lat': 12.9165,
        'lng': 77.6101,
        'zone': zone_b,
        'capacity': 90,
    },
]

partners = []
partner_group = created_groups['Partner']

for p_data in partners_data:
    # Create user account for partner
    user, created = User.objects.get_or_create(
        email=p_data['email'],
        defaults={
            'first_name': p_data['contact_person'].split()[0],
            'last_name': p_data['contact_person'].split()[-1],
            'phone': p_data['contact_phone'],
            'user_type': 'partner',
            'is_active': True,
            'is_verified': True,
        }
    )

    if created:
        user.set_password('partner123')
        user.save()
        user.groups.add(partner_group)

    # Create partner business profile
    partner, partner_created = Partner.objects.get_or_create(
        user=user,
        defaults={
            'business_name': p_data['business_name'],
            'business_type': p_data['business_type'],
            'business_registration_number': f"REG{random.randint(100000, 999999)}",
            'tax_id': f"GSTIN{random.randint(10000000, 99999999)}",
            'contact_person': p_data['contact_person'],
            'contact_email': p_data['email'],
            'contact_phone': p_data['contact_phone'],
            'address_line1': f"{random.randint(10, 99)}, Main Road",
            'address_line2': p_data['area'],
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': p_data['pincode'],
            'latitude': Decimal(str(p_data['lat'])),
            'longitude': Decimal(str(p_data['lng'])),
            'pricing_zone': p_data['zone'],
            'service_radius': Decimal('5.0'),
            'daily_capacity': p_data['capacity'],
            'current_load': random.randint(0, p_data['capacity'] // 2),
            'status': 'active',
            'is_verified': True,
            'verified_at': timezone.now() - timedelta(days=random.randint(30, 90)),
            'onboarded_at': timezone.now() - timedelta(days=random.randint(30, 90)),
            'average_rating': Decimal(str(round(random.uniform(4.0, 5.0), 2))),
            'total_ratings': random.randint(50, 200),
            'completed_orders': random.randint(100, 500),
            'cancelled_orders': random.randint(5, 20),
            'total_revenue': Decimal(str(random.randint(50000, 200000))),
            'commission_rate': Decimal('15.00'),
            'description': f"Professional laundry service in {p_data['area']} with {random.randint(5, 15)} years of experience.",
            'bank_name': random.choice(['HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank']),
            'account_holder_name': p_data['contact_person'],
            'account_number': f"{random.randint(100000000000, 999999999999)}",
            'ifsc_code': f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=11))}",
            'upi_id': f"{p_data['email'].split('@')[0]}@upi",
        }
    )

    if partner_created:
        partners.append(partner)
        print(f"  ✓ {p_data['business_name']} ({p_data['area']})")

print(f"  Total: {len(partners)} partner businesses")

# =============================================================================
# 8. CREATE PARTNER AVAILABILITY SCHEDULES
# =============================================================================
print("\n[8/12] Creating partner availability schedules...")

availability_created = 0
for partner in partners:
    # Monday to Saturday: 9 AM - 9 PM
    for weekday in range(6):  # 0 = Monday, 5 = Saturday
        PartnerAvailability.objects.get_or_create(
            partner=partner,
            weekday=weekday,
            defaults={
                'is_available': True,
                'start_time': time(9, 0),
                'end_time': time(21, 0),
            }
        )
        availability_created += 1

    # Sunday: 10 AM - 6 PM (reduced hours)
    PartnerAvailability.objects.get_or_create(
        partner=partner,
        weekday=6,  # Sunday
        defaults={
            'is_available': True,
            'start_time': time(10, 0),
            'end_time': time(18, 0),
        }
    )
    availability_created += 1

print(f"  ✓ Created {availability_created} availability slots")

# =============================================================================
# 9. CREATE PARTNER SERVICE AREAS
# =============================================================================
print("\n[9/12] Creating partner service areas...")

# Define service areas for each partner
service_areas_map = {
    0: [  # CleanPro - Indiranagar (Zone A)
        ('560038', 'Indiranagar', 'Bangalore', Decimal('0')),
        ('560008', 'Domlur', 'Bangalore', Decimal('30')),
        ('560005', 'HAL 2nd Stage', 'Bangalore', Decimal('40')),
    ],
    1: [  # Sparkle - Koramangala (Zone B)
        ('560095', 'Koramangala 1st Block', 'Bangalore', Decimal('0')),
        ('560034', 'Koramangala 5th Block', 'Bangalore', Decimal('0')),
        ('560047', 'Koramangala 7th Block', 'Bangalore', Decimal('20')),
    ],
    2: [  # Fresh & Clean - HSR (Zone C)
        ('560102', 'HSR Layout Sector 1', 'Bangalore', Decimal('0')),
        ('560068', 'HSR Layout Sector 2', 'Bangalore', Decimal('0')),
        ('560076', 'BTM Layout', 'Bangalore', Decimal('50')),
    ],
    3: [  # Premium Care - Whitefield (Zone A)
        ('560066', 'Whitefield', 'Bangalore', Decimal('0')),
        ('560048', 'Marathahalli', 'Bangalore', Decimal('40')),
        ('560037', 'Bellandur', 'Bangalore', Decimal('50')),
    ],
    4: [  # Express - BTM (Zone B)
        ('560076', 'BTM Layout Stage 1', 'Bangalore', Decimal('0')),
        ('560029', 'BTM Layout Stage 2', 'Bangalore', Decimal('0')),
        ('560068', 'HSR Layout', 'Bangalore', Decimal('30')),
    ],
}

service_areas_created = 0
for idx, partner in enumerate(partners):
    if idx in service_areas_map:
        for pincode, area_name, city, extra_charge in service_areas_map[idx]:
            PartnerServiceArea.objects.get_or_create(
                partner=partner,
                pincode=pincode,
                defaults={
                    'area_name': area_name,
                    'city': city,
                    'is_active': True,
                    'extra_delivery_charge': extra_charge,
                }
            )
            service_areas_created += 1

print(f"  ✓ Created {service_areas_created} service area mappings")

# =============================================================================
# 10. CREATE SAMPLE ORDERS WITH ITEMS
# =============================================================================
print("\n[10/12] Creating sample orders...")

statuses = ['pending', 'confirmed', 'picked_up', 'in_progress', 'ready', 'delivered', 'completed']
payment_methods = ['online', 'cod', 'wallet']
all_services = list(Service.objects.filter(is_active=True))

orders_created = 0
for i in range(30):  # Create 30 orders
    customer = random.choice(customers)
    partner = random.choice(partners)
    customer_address = Address.objects.filter(user=customer).first()

    if not customer_address:
        continue

    # Create order
    order_date = timezone.now() - timedelta(days=random.randint(0, 30))
    status = random.choice(statuses)

    # Calculate dates based on status
    pickup_date = order_date + timedelta(hours=random.randint(2, 24))
    delivery_date = pickup_date + timedelta(days=random.randint(1, 3))

    order, created = Order.objects.get_or_create(
        order_number=f"ORD{timezone.now().strftime('%Y%m')}{str(i+1).zfill(4)}",
        defaults={
            'customer': customer,
            'partner': partner,
            'pickup_address': customer_address,
            'delivery_address': customer_address,
            'pickup_date': pickup_date,
            'delivery_date': delivery_date,
            'status': status,
            'payment_method': random.choice(payment_methods),
            'payment_status': 'paid' if status in ['delivered', 'completed'] else 'pending',
            'special_instructions': random.choice(['', 'Handle with care', 'Rush order', 'Fragile items']),
            'created_at': order_date,
        }
    )

    if created:
        # Add order items
        num_items = random.randint(2, 6)
        subtotal = Decimal('0')

        for _ in range(num_items):
            service = random.choice(all_services)
            quantity = random.randint(1, 5)

            # Get pricing for the partner's zone
            pricing = ServicePricing.objects.filter(
                service=service,
                zone=partner.pricing_zone
            ).first()

            if pricing:
                unit_price = pricing.discount_price if pricing.discount_price else pricing.base_price

                OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity,
                )
                subtotal += unit_price * quantity

        # Update order totals
        delivery_fee = Decimal('50')
        tax_rate = Decimal('0.18')  # 18% GST
        tax_amount = subtotal * tax_rate

        order.subtotal = subtotal
        order.delivery_fee = delivery_fee
        order.tax_amount = tax_amount
        order.total_amount = subtotal + delivery_fee + tax_amount
        order.save()

        orders_created += 1

print(f"  ✓ Created {orders_created} orders with items")

# =============================================================================
# 11. CREATE PAYMENTS AND TRANSACTIONS
# =============================================================================
print("\n[11/12] Creating payments and transactions...")

payments_created = 0
completed_orders = Order.objects.filter(status__in=['delivered', 'completed'])

for order in completed_orders:
    # Create payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_amount,
            'payment_method': order.payment_method,
            'payment_gateway': random.choice(['razorpay', 'paytm', 'phonepe']) if order.payment_method == 'online' else None,
            'transaction_id': f"TXN{random.randint(1000000000, 9999999999)}" if order.payment_method == 'online' else None,
            'status': 'completed',
            'payment_date': order.created_at + timedelta(hours=1),
        }
    )

    if created:
        # Create wallet transaction record if wallet payment
        if order.payment_method == 'wallet':
            wallet = Wallet.objects.get(user=order.customer)
            WalletTransaction.objects.get_or_create(
                wallet=wallet,
                transaction_type='debit',
                amount=order.total_amount,
                defaults={
                    'description': f'Payment for order {order.order_number}',
                    'status': 'completed',
                    'related_order': order,
                }
            )
            # Deduct from wallet balance
            if wallet.balance >= order.total_amount:
                wallet.balance -= order.total_amount
                wallet.save()

        payments_created += 1

print(f"  ✓ Created {payments_created} payment records")

# =============================================================================
# 12. CREATE CHAT ROOMS AND MESSAGES
# =============================================================================
print("\n[12/12] Creating chat rooms and sample messages...")

chats_created = 0
messages_created = 0

# Create chat rooms for some orders
sample_orders = Order.objects.filter(status__in=['confirmed', 'picked_up', 'in_progress', 'ready'])[:10]

for order in sample_orders:
    chat_room, created = ChatRoom.objects.get_or_create(
        order=order,
        defaults={
            'customer': order.customer,
            'partner': order.partner,
            'is_active': True,
        }
    )

    if created:
        chats_created += 1

        # Create sample messages
        sample_messages = [
            (order.customer, "Hi, when will you pick up my order?", 0),
            (order.partner.user, "Hello! We'll pick up today between 2-4 PM.", 5),
            (order.customer, "Perfect, thank you!", 10),
            (order.partner.user, "Your order has been picked up successfully.", 120),
        ]

        for sender, message, minutes_offset in sample_messages:
            ChatMessage.objects.create(
                room=chat_room,
                sender=sender,
                message=message,
                created_at=order.created_at + timedelta(minutes=minutes_offset),
            )
            messages_created += 1

print(f"  ✓ Created {chats_created} chat rooms with {messages_created} messages")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("DEMO DATA SEEDING COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\n📊 Summary:")
print(f"  • {len(created_groups)} User Groups")
print(f"  • {len(zones)} Pricing Zones")
print(f"  • {len(categories)} Service Categories")
print(f"  • {Service.objects.count()} Services with zone-based pricing")
print(f"  • {len(customers)} Customers with addresses")
print(f"  • {len(partners)} Partner Businesses")
print(f"  • {PartnerAvailability.objects.count()} Availability Schedules")
print(f"  • {PartnerServiceArea.objects.count()} Service Area Mappings")
print(f"  • {Order.objects.count()} Orders with items")
print(f"  • {Payment.objects.count()} Payment Records")
print(f"  • {ChatRoom.objects.count()} Chat Rooms")
print(f"  • {ChatMessage.objects.count()} Chat Messages")

print("\n🔑 Partner Login Credentials:")
for idx, partner in enumerate(partners):
    print(f"  {idx+1}. {partner.business_name}")
    print(f"     Email: {partner.user.email}")
    print(f"     Password: partner123")
    print(f"     Location: {partner.address_line2}, {partner.city}")
    print()

print("🔑 Customer Login:")
print("  Email: demo.customer@test.com")
print("  Password: demo123")

print("\n🔑 Admin Login:")
print("  Email: admin@laundryconnect.com")
print("  Password: admin123")

print("\n✅ Ready for partner-focused demo and testing!")
print("=" * 80)
