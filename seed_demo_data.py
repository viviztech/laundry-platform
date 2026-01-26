"""
Comprehensive seed script for LaundryConnect with Groups and Permissions
Run with: python manage.py shell < seed_demo_data.py
"""
from django.utils.text import slugify
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import random
from apps.accounts.models import User, UserProfile, Address
from apps.services.models import ServiceCategory, GarmentType, Service, PricingZone, ServicePricing
from apps.partners.models import Partner, PartnerAvailability
from apps.orders.models import Order, OrderItem
from apps.payments.models import Wallet

print("=" * 60)
print("SEEDING LAUNDRYCONNECT DEMO DATA")
print("=" * 60)

# =============================================================================
# 1. CREATE USER GROUPS WITH PERMISSIONS
# =============================================================================
print("\n1. Creating user groups and permissions...")

# Define groups and their permissions
groups_config = {
    'Customer': {
        'description': 'Regular customers who place orders',
        'permissions': [
            ('orders', 'order', ['add', 'view', 'change']),  # Can create and view their orders
            ('accounts', 'address', ['add', 'view', 'change', 'delete']),  # Manage their addresses
            ('payments', 'wallet', ['view']),  # View their wallet
        ]
    },
    'Partner': {
        'description': 'Laundry service partners',
        'permissions': [
            ('partners', 'partner', ['view', 'change']),  # View and update their profile
            ('orders', 'order', ['view', 'change']),  # View and update assigned orders
            ('partners', 'partneravailability', ['add', 'view', 'change', 'delete']),  # Manage availability
        ]
    },
    'Admin': {
        'description': 'Platform administrators',
        'permissions': [
            ('orders', 'order', ['add', 'view', 'change', 'delete']),
            ('accounts', 'user', ['view', 'change']),
            ('partners', 'partner', ['add', 'view', 'change', 'delete']),
            ('services', 'service', ['add', 'view', 'change', 'delete']),
            ('services', 'servicecategory', ['add', 'view', 'change', 'delete']),
            ('services', 'pricingzone', ['add', 'view', 'change', 'delete']),
            ('payments', 'wallet', ['view', 'change']),
        ]
    },
    'Support': {
        'description': 'Customer support staff',
        'permissions': [
            ('orders', 'order', ['view', 'change']),
            ('accounts', 'user', ['view']),
            ('partners', 'partner', ['view']),
        ]
    },
}

created_groups = {}
for group_name, config in groups_config.items():
    group, created = Group.objects.get_or_create(name=group_name)

    if created:
        # Add permissions to the group
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

print(f"Created {len(created_groups)} groups")

# =============================================================================
# 2. CREATE PRICING ZONES
# =============================================================================
print("\n2. Creating pricing zones...")
zone_a, _ = PricingZone.objects.get_or_create(
    zone='A',
    defaults={'name': 'Zone A - Premium', 'description': 'Premium areas with higher pricing', 'multiplier': Decimal('1.2')}
)
zone_b, _ = PricingZone.objects.get_or_create(
    zone='B',
    defaults={'name': 'Zone B - Standard', 'description': 'Standard residential areas', 'multiplier': Decimal('1.0')}
)
zone_c, _ = PricingZone.objects.get_or_create(
    zone='C',
    defaults={'name': 'Zone C - Economy', 'description': 'Economy areas with competitive pricing', 'multiplier': Decimal('0.9')}
)
zones = [zone_a, zone_b, zone_c]
print(f"  ✓ Created {len(zones)} pricing zones")

# =============================================================================
# 3. CREATE SERVICE CATEGORIES
# =============================================================================
print("\n3. Creating service categories...")
categories_data = [
    {'name': 'Wash & Iron', 'description': 'Complete washing and ironing service for all garments', 'icon': 'wash_iron', 'display_order': 1},
    {'name': 'Dry Cleaning', 'description': 'Professional dry cleaning for delicate fabrics', 'icon': 'dry_clean', 'display_order': 2},
    {'name': 'Iron Only', 'description': 'Quick ironing service for clean clothes', 'icon': 'iron_press', 'display_order': 3},
    {'name': 'Wash Only', 'description': 'Washing service without ironing', 'icon': 'wash_fold', 'display_order': 4},
    {'name': 'Premium Care', 'description': 'Special care for premium and designer garments', 'icon': 'premium', 'display_order': 5},
]

categories = []
for cat_data in categories_data:
    cat, _ = ServiceCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={**cat_data, 'slug': slugify(cat_data['name'])}
    )
    categories.append(cat)
print(f"  ✓ Created {len(categories)} categories")

# =============================================================================
# 4. CREATE GARMENT TYPES
# =============================================================================
print("\n4. Creating garment types...")
garments_data = [
    # Wash & Iron
    {'name': 'Shirt', 'category': categories[0]},
    {'name': 'T-Shirt', 'category': categories[0]},
    {'name': 'Jeans', 'category': categories[0]},
    {'name': 'Trousers', 'category': categories[0]},
    {'name': 'Saree', 'category': categories[0]},
    {'name': 'Kurta', 'category': categories[0]},
    # Dry Cleaning
    {'name': 'Suit (2-piece)', 'category': categories[1]},
    {'name': 'Suit (3-piece)', 'category': categories[1]},
    {'name': 'Blazer', 'category': categories[1]},
    {'name': 'Dress', 'category': categories[1]},
    {'name': 'Wedding Attire', 'category': categories[4]},
]

garments = []
for gar_data in garments_data:
    gar, _ = GarmentType.objects.get_or_create(
        name=gar_data['name'],
        defaults={'slug': slugify(gar_data['name']), 'category': gar_data['category']}
    )
    garments.append(gar)
print(f"  ✓ Created {len(garments)} garment types")

# =============================================================================
# 5. CREATE SERVICES WITH PRICING
# =============================================================================
print("\n5. Creating services with pricing...")
services_data = [
    {'category': categories[0], 'garment': garments[0], 'name': 'Wash & Iron - Shirt', 'base_price': 30},
    {'category': categories[0], 'garment': garments[1], 'name': 'Wash & Iron - T-Shirt', 'base_price': 25},
    {'category': categories[0], 'garment': garments[2], 'name': 'Wash & Iron - Jeans', 'base_price': 50},
    {'category': categories[0], 'garment': garments[3], 'name': 'Wash & Iron - Trousers', 'base_price': 40},
    {'category': categories[0], 'garment': garments[4], 'name': 'Wash & Iron - Saree', 'base_price': 80},
    {'category': categories[0], 'garment': garments[5], 'name': 'Wash & Iron - Kurta', 'base_price': 45},
    {'category': categories[1], 'garment': garments[6], 'name': 'Dry Clean - Suit (2-piece)', 'base_price': 300},
    {'category': categories[1], 'garment': garments[7], 'name': 'Dry Clean - Suit (3-piece)', 'base_price': 400},
    {'category': categories[1], 'garment': garments[8], 'name': 'Dry Clean - Blazer', 'base_price': 200},
    {'category': categories[1], 'garment': garments[9], 'name': 'Dry Clean - Dress', 'base_price': 150},
    {'category': categories[4], 'garment': garments[10], 'name': 'Premium Care - Wedding Attire', 'base_price': 800},
]

services = []
for svc_data in services_data:
    svc, created = Service.objects.get_or_create(
        category=svc_data['category'],
        garment=svc_data['garment'],
        defaults={
            'name': svc_data['name'],
            'description': f"Professional {svc_data['category'].name.lower()} service for {svc_data['garment'].name}",
            'turnaround_time': 'express' if 'Premium' in svc_data['category'].name else 'standard'
        }
    )

    if created:
        # Create pricing for each zone
        for zone in zones:
            ServicePricing.objects.create(
                service=svc,
                zone=zone,
                base_price=Decimal(svc_data['base_price']) * zone.multiplier,
                discount_price=Decimal(svc_data['base_price']) * zone.multiplier * Decimal('0.9'),
            )
    services.append(svc)
print(f"  ✓ Created {len(services)} services with zone-based pricing")

# =============================================================================
# 6. CREATE DEMO USERS (CUSTOMERS)
# =============================================================================
print("\n6. Creating customer users...")
customers_data = [
    {'email': 'demo.customer@test.com', 'first_name': 'Demo', 'last_name': 'Customer', 'phone': '+919000000001'},
    {'email': 'rajesh.kumar@gmail.com', 'first_name': 'Rajesh', 'last_name': 'Kumar', 'phone': '+919000000002'},
    {'email': 'priya.sharma@gmail.com', 'first_name': 'Priya', 'last_name': 'Sharma', 'phone': '+919000000003'},
    {'email': 'amit.patel@gmail.com', 'first_name': 'Amit', 'last_name': 'Patel', 'phone': '+919000000004'},
    {'email': 'sneha.reddy@gmail.com', 'first_name': 'Sneha', 'last_name': 'Reddy', 'phone': '+919000000005'},
]

customers = []
addresses_list = [
    ('Home', '123 MG Road', 'Bangalore', '560001'),
    ('Office', '456 Whitefield Main Road', 'Bangalore', '560066'),
]

for idx, user_data in enumerate(customers_data):
    existing_user = User.objects.filter(email=user_data['email']).first() or User.objects.filter(phone=user_data['phone']).first()

    if not existing_user:
        user = User.objects.create_user(
            email=user_data['email'],
            password='demo123',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            user_type='customer',
            is_verified=True,
        )

        # Add to Customer group
        user.groups.add(created_groups['Customer'])

        # Create profile
        UserProfile.objects.create(
            user=user,
            gender=random.choice(['male', 'female']),
            preferred_language='en',
            receive_notifications=True,
        )

        # Create 1-2 addresses
        num_addresses = random.randint(1, 2)
        for i in range(num_addresses):
            addr_data = addresses_list[i]
            Address.objects.create(
                user=user,
                label=addr_data[0],
                address_line1=addr_data[1],
                city=addr_data[2],
                state='Karnataka',
                pincode=addr_data[3],
                country='India',
                contact_name=user.get_full_name(),
                contact_phone=user.phone,
                is_default=(i == 0),
                latitude=Decimal('12.9716') + Decimal(random.uniform(-0.05, 0.05)),
                longitude=Decimal('77.5946') + Decimal(random.uniform(-0.05, 0.05)),
            )

        # Create wallet with some balance
        Wallet.objects.create(
            user=user,
            balance=Decimal(random.randint(0, 500))
        )

        customers.append(user)

print(f"  ✓ Created {len(customers)} customer accounts with addresses and wallets")

# =============================================================================
# 7. CREATE PARTNER USERS
# =============================================================================
print("\n7. Creating partner users and businesses...")
partners_data = [
    {
        'email': 'cleanpro@business.com',
        'first_name': 'CleanPro',
        'last_name': 'Services',
        'phone': '+919100000001',
        'business_name': 'CleanPro Laundry Services',
        'business_type': 'laundry',
        'address': '123 Indiranagar Main Road',
        'city': 'Bangalore',
        'pincode': '560038',
        'zone': zone_a,
    },
    {
        'email': 'sparklewash@business.com',
        'first_name': 'Sparkle',
        'last_name': 'Wash',
        'phone': '+919100000002',
        'business_name': 'Sparkle Wash & Dry',
        'business_type': 'dry_cleaning',
        'address': '456 Koramangala 4th Block',
        'city': 'Bangalore',
        'pincode': '560034',
        'zone': zone_b,
    },
    {
        'email': 'freshclean@business.com',
        'first_name': 'Fresh',
        'last_name': 'Clean',
        'phone': '+919100000003',
        'business_name': 'Fresh & Clean Laundry',
        'business_type': 'laundry',
        'address': '789 HSR Layout',
        'city': 'Bangalore',
        'pincode': '560102',
        'zone': zone_c,
    },
]

partners = []
for partner_data in partners_data:
    existing_user = User.objects.filter(email=partner_data['email']).first() or User.objects.filter(phone=partner_data['phone']).first()

    if not existing_user:
        user = User.objects.create_user(
            email=partner_data['email'],
            password='partner123',
            first_name=partner_data['first_name'],
            last_name=partner_data['last_name'],
            phone=partner_data['phone'],
            user_type='partner',
            is_verified=True,
        )

        # Add to Partner group
        user.groups.add(created_groups['Partner'])

        # Create partner profile
        partner = Partner.objects.create(
            user=user,
            business_name=partner_data['business_name'],
            business_type=partner_data['business_type'],
            address_line1=partner_data['address'],
            city=partner_data['city'],
            state='Karnataka',
            pincode=partner_data['pincode'],
            pricing_zone=partner_data['zone'],
            service_radius=10,
            daily_capacity=random.randint(80, 120),
            status='active',
            is_verified=True,
            commission_rate=Decimal('15.0'),
            latitude=Decimal('12.9716') + Decimal(random.uniform(-0.1, 0.1)),
            longitude=Decimal('77.5946') + Decimal(random.uniform(-0.1, 0.1)),
            average_rating=Decimal(random.uniform(4.0, 5.0)),
            total_ratings=random.randint(50, 200),
            completed_orders=random.randint(100, 500),
        )

        # Create availability schedule (Mon-Sat, 9 AM - 9 PM)
        # weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        for weekday in range(6):  # Monday to Saturday (0-5)
            PartnerAvailability.objects.create(
                partner=partner,
                weekday=weekday,
                start_time='09:00:00',
                end_time='21:00:00',
                is_available=True,
            )

        partners.append(partner)

print(f"  ✓ Created {len(partners)} partner accounts with business profiles")

# =============================================================================
# 8. CREATE ADMIN AND SUPPORT USERS
# =============================================================================
print("\n8. Creating admin and support staff...")
staff_users = [
    {
        'email': 'admin@laundryconnect.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'phone': '+919200000001',
        'group': 'Admin',
        'is_staff': True,
    },
    {
        'email': 'support@laundryconnect.com',
        'first_name': 'Support',
        'last_name': 'Agent',
        'phone': '+919200000002',
        'group': 'Support',
        'is_staff': True,
    },
]

staff_created = 0
for staff_data in staff_users:
    existing_user = User.objects.filter(email=staff_data['email']).first()

    if not existing_user:
        user = User.objects.create_user(
            email=staff_data['email'],
            password='admin123',
            first_name=staff_data['first_name'],
            last_name=staff_data['last_name'],
            phone=staff_data['phone'],
            user_type='customer',
            is_verified=True,
            is_staff=staff_data['is_staff'],
        )
        user.groups.add(created_groups[staff_data['group']])
        staff_created += 1

print(f"  ✓ Created {staff_created} staff accounts")

# =============================================================================
# 9. CREATE SAMPLE ORDERS
# =============================================================================
print("\n9. Creating sample orders...")
from django.utils import timezone
from datetime import timedelta

if customers and partners:
    order_statuses = ['pending', 'confirmed', 'picked_up', 'in_progress', 'ready', 'delivered']
    orders_created = 0

    for i in range(15):  # Create 15 sample orders
        customer = random.choice(customers)
        partner = random.choice(partners)

        # Get customer's default address
        address = Address.objects.filter(user=customer, is_default=True).first()
        if not address:
            continue

        status = random.choice(order_statuses)
        created_at = timezone.now() - timedelta(days=random.randint(0, 30))

        order = Order.objects.create(
            user=customer,
            pickup_address=address,
            delivery_address=address,
            status=status,
            payment_status='completed' if status == 'delivered' else 'pending',
            payment_method=random.choice(['razorpay', 'wallet', 'cod']),
            pickup_date=created_at.date(),
            pickup_time_slot='morning',
            delivery_date=(created_at + timedelta(days=2)).date(),
            delivery_time_slot='evening',
            assigned_partner=partner if status != 'pending' else None,
            created_at=created_at,
        )

        # Add order items
        num_items = random.randint(2, 5)
        selected_services = random.sample(services, min(num_items, len(services)))

        subtotal = Decimal('0')
        for service in selected_services:
            quantity = random.randint(1, 3)
            pricing = ServicePricing.objects.filter(service=service, zone=partner.pricing_zone).first()

            if pricing:
                unit_price = pricing.base_price
                item_total = unit_price * quantity
                subtotal += item_total

                OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=item_total,
                )

        # Calculate totals
        tax_amount = subtotal * Decimal('0.18')  # 18% GST
        delivery_fee = Decimal('50') if subtotal < 500 else Decimal('0')
        total = subtotal + tax_amount + delivery_fee

        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.delivery_fee = delivery_fee
        order.total_amount = total

        if status == 'delivered':
            order.completed_at = created_at + timedelta(days=2)

        order.save()
        orders_created += 1

    print(f"  ✓ Created {orders_created} sample orders")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("✅ DEMO DATA SEEDED SUCCESSFULLY!")
print("=" * 60)

print("\n📊 Summary:")
print(f"  • User Groups: {len(created_groups)}")
print(f"  • Pricing Zones: {len(zones)}")
print(f"  • Service Categories: {len(categories)}")
print(f"  • Garment Types: {len(garments)}")
print(f"  • Services: {len(services)}")
print(f"  • Customer Accounts: {len(customers)}")
print(f"  • Partner Accounts: {len(partners)}")
print(f"  • Sample Orders: {orders_created if 'orders_created' in locals() else 0}")

print("\n🔐 Demo Login Credentials:")
print("\n  Customer:")
print("    Email: demo.customer@test.com")
print("    Password: demo123")
print("\n  Partner:")
print("    Email: cleanpro@business.com")
print("    Password: partner123")
print("\n  Admin:")
print("    Email: admin@laundryconnect.com")
print("    Password: admin123")
print("\n  Support:")
print("    Email: support@laundryconnect.com")
print("    Password: admin123")

print("\n" + "=" * 60)
