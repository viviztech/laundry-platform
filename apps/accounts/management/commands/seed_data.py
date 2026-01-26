"""
Seed realistic data for LaundryConnect platform
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
from datetime import timedelta
import random

from apps.accounts.models import User, UserProfile, Address
from apps.services.models import ServiceCategory, Service, PricingZone, ServicePricing
from apps.partners.models import Partner, PartnerAvailability
from apps.orders.models import Order, OrderItem
from apps.payments.models import Wallet
from apps.notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Seed database with realistic laundry service data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Seeding data...')

        with transaction.atomic():
            # Seed in order of dependencies
            users = self.seed_users()
            zones = self.seed_pricing_zones()
            categories = self.seed_service_categories()
            services = self.seed_services(categories, zones)
            partners = self.seed_partners(users, zones)
            self.seed_partner_availability(partners)
            orders = self.seed_orders(users, services, partners)
            self.seed_wallets(users)
            self.seed_notification_templates()

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def clear_data(self):
        """Clear existing data"""
        # Clear in reverse order of dependencies
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        # WalletTransaction.objects.all().delete()
        Wallet.objects.all().delete()
        PartnerAvailability.objects.all().delete()
        Partner.objects.all().delete()
        ServicePricing.objects.all().delete()
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
        PricingZone.objects.all().delete()
        Address.objects.all().delete()
        UserProfile.objects.all().delete()
        NotificationTemplate.objects.all().delete()
        # Don't delete superusers
        User.objects.filter(is_superuser=False).delete()

    def seed_users(self):
        """Create realistic users"""
        self.stdout.write('Creating users...')

        users = []

        # Customer users
        customer_data = [
            {'email': 'rajesh.kumar@gmail.com', 'first_name': 'Rajesh', 'last_name': 'Kumar', 'phone': '+919876543210'},
            {'email': 'priya.sharma@yahoo.com', 'first_name': 'Priya', 'last_name': 'Sharma', 'phone': '+919876543211'},
            {'email': 'amit.patel@outlook.com', 'first_name': 'Amit', 'last_name': 'Patel', 'phone': '+919876543212'},
            {'email': 'sneha.reddy@gmail.com', 'first_name': 'Sneha', 'last_name': 'Reddy', 'phone': '+919876543213'},
            {'email': 'vikram.singh@gmail.com', 'first_name': 'Vikram', 'last_name': 'Singh', 'phone': '+919876543214'},
            {'email': 'anita.mehta@gmail.com', 'first_name': 'Anita', 'last_name': 'Mehta', 'phone': '+919876543215'},
            {'email': 'rahul.verma@gmail.com', 'first_name': 'Rahul', 'last_name': 'Verma', 'phone': '+919876543216'},
            {'email': 'deepika.joshi@gmail.com', 'first_name': 'Deepika', 'last_name': 'Joshi', 'phone': '+919876543217'},
        ]

        for data in customer_data:
            try:
                user = User.objects.get(email=data['email'])
                created = False
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=data['email'],
                    password='password123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data['phone'],
                    user_type='customer',
                    is_verified=True,
                )
                created = True

                # Create profile
                UserProfile.objects.create(
                    user=user,
                    gender=random.choice(['male', 'female']),
                    preferred_language='en',
                    receive_notifications=True,
                )

                # Create addresses
                self.create_user_addresses(user)

            users.append(user)

        # Partner users
        partner_data = [
            {'email': 'cleanpro.laundry@business.com', 'first_name': 'Clean', 'last_name': 'Pro', 'phone': '+919876540001'},
            {'email': 'sparkle.wash@business.com', 'first_name': 'Sparkle', 'last_name': 'Wash', 'phone': '+919876540002'},
            {'email': 'fresh.clean@business.com', 'first_name': 'Fresh', 'last_name': 'Clean', 'phone': '+919876540003'},
            {'email': 'premium.laundry@business.com', 'first_name': 'Premium', 'last_name': 'Laundry', 'phone': '+919876540004'},
        ]

        for data in partner_data:
            try:
                user = User.objects.get(email=data['email'])
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=data['email'],
                    password='password123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data['phone'],
                    user_type='partner',
                    is_verified=True,
                )
            users.append(user)

        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_user_addresses(self, user):
        """Create addresses for a user"""
        addresses = [
            {
                'label': 'Home',
                'address_line1': f'{random.randint(1, 999)} MG Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001',
                'is_default': True,
            },
            {
                'label': 'Office',
                'address_line1': f'{random.randint(1, 999)} Whitefield',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560066',
                'is_default': False,
            },
        ]

        for addr_data in addresses:
            Address.objects.create(
                user=user,
                **addr_data,
                contact_name=user.get_full_name(),
                contact_phone=user.phone,
                country='India',
                latitude=Decimal('12.9716') + Decimal(random.uniform(-0.1, 0.1)),
                longitude=Decimal('77.5946') + Decimal(random.uniform(-0.1, 0.1)),
            )

    def seed_pricing_zones(self):
        """Create pricing zones"""
        self.stdout.write('Creating pricing zones...')

        zones_data = [
            {'zone': 'A', 'name': 'Zone A - Premium', 'description': 'Premium areas with higher pricing', 'multiplier': Decimal('1.2')},
            {'zone': 'B', 'name': 'Zone B - Standard', 'description': 'Standard residential areas', 'multiplier': Decimal('1.0')},
            {'zone': 'C', 'name': 'Zone C - Economy', 'description': 'Economy areas with competitive pricing', 'multiplier': Decimal('0.9')},
        ]

        zones = []
        for data in zones_data:
            zone, _ = PricingZone.objects.get_or_create(
                zone=data['zone'],
                defaults=data
            )
            zones.append(zone)

        self.stdout.write(f'Created {len(zones)} pricing zones')
        return zones

    def seed_service_categories(self):
        """Create service categories"""
        self.stdout.write('Creating service categories...')

        categories_data = [
            {
                'name': 'Wash & Iron',
                'description': 'Complete washing and ironing service for all garments',
                'icon': '👔',
                'display_order': 1,
            },
            {
                'name': 'Dry Cleaning',
                'description': 'Professional dry cleaning for delicate fabrics',
                'icon': '🧥',
                'display_order': 2,
            },
            {
                'name': 'Iron Only',
                'description': 'Quick ironing service for clean clothes',
                'icon': '🔥',
                'display_order': 3,
            },
            {
                'name': 'Wash Only',
                'description': 'Washing service without ironing',
                'icon': '🧼',
                'display_order': 4,
            },
            {
                'name': 'Premium Care',
                'description': 'Special care for premium and designer garments',
                'icon': '⭐',
                'display_order': 5,
            },
            {
                'name': 'Home Essentials',
                'description': 'Curtains, bedsheets, and household items',
                'icon': '🏠',
                'display_order': 6,
            },
        ]

        categories = []
        for data in categories_data:
            # Add slug if not present
            if 'slug' not in data:
                data['slug'] = slugify(data['name'])

            category, _ = ServiceCategory.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            categories.append(category)

        self.stdout.write(f'Created {len(categories)} categories')
        return categories

    def seed_services(self, categories, zones):
        """Create services with pricing"""
        self.stdout.write('Creating services...')

        # Map categories for easy access
        category_map = {cat.name: cat for cat in categories}

        services_data = [
            # Wash & Iron
            {'category': 'Wash & Iron', 'name': 'Shirt', 'unit': 'piece', 'base_price': 30},
            {'category': 'Wash & Iron', 'name': 'T-Shirt', 'unit': 'piece', 'base_price': 25},
            {'category': 'Wash & Iron', 'name': 'Jeans', 'unit': 'piece', 'base_price': 50},
            {'category': 'Wash & Iron', 'name': 'Trousers', 'unit': 'piece', 'base_price': 40},
            {'category': 'Wash & Iron', 'name': 'Saree', 'unit': 'piece', 'base_price': 80},
            {'category': 'Wash & Iron', 'name': 'Kurta', 'unit': 'piece', 'base_price': 45},
            {'category': 'Wash & Iron', 'name': 'Salwar Kameez', 'unit': 'set', 'base_price': 90},

            # Dry Cleaning
            {'category': 'Dry Cleaning', 'name': 'Suit (2 piece)', 'unit': 'set', 'base_price': 300},
            {'category': 'Dry Cleaning', 'name': 'Suit (3 piece)', 'unit': 'set', 'base_price': 400},
            {'category': 'Dry Cleaning', 'name': 'Blazer', 'unit': 'piece', 'base_price': 200},
            {'category': 'Dry Cleaning', 'name': 'Coat', 'unit': 'piece', 'base_price': 250},
            {'category': 'Dry Cleaning', 'name': 'Jacket', 'unit': 'piece', 'base_price': 180},
            {'category': 'Dry Cleaning', 'name': 'Dress', 'unit': 'piece', 'base_price': 150},
            {'category': 'Dry Cleaning', 'name': 'Silk Saree', 'unit': 'piece', 'base_price': 200},

            # Iron Only
            {'category': 'Iron Only', 'name': 'Shirt', 'unit': 'piece', 'base_price': 15},
            {'category': 'Iron Only', 'name': 'T-Shirt', 'unit': 'piece', 'base_price': 12},
            {'category': 'Iron Only', 'name': 'Jeans', 'unit': 'piece', 'base_price': 20},
            {'category': 'Iron Only', 'name': 'Trousers', 'unit': 'piece', 'base_price': 18},
            {'category': 'Iron Only', 'name': 'Saree', 'unit': 'piece', 'base_price': 40},

            # Wash Only
            {'category': 'Wash Only', 'name': 'Shirt', 'unit': 'piece', 'base_price': 20},
            {'category': 'Wash Only', 'name': 'T-Shirt', 'unit': 'piece', 'base_price': 15},
            {'category': 'Wash Only', 'name': 'Jeans', 'unit': 'piece', 'base_price': 35},
            {'category': 'Wash Only', 'name': 'Trousers', 'unit': 'piece', 'base_price': 25},

            # Premium Care
            {'category': 'Premium Care', 'name': 'Designer Suit', 'unit': 'piece', 'base_price': 600},
            {'category': 'Premium Care', 'name': 'Designer Dress', 'unit': 'piece', 'base_price': 400},
            {'category': 'Premium Care', 'name': 'Wedding Attire', 'unit': 'piece', 'base_price': 800},
            {'category': 'Premium Care', 'name': 'Leather Jacket', 'unit': 'piece', 'base_price': 500},

            # Home Essentials
            {'category': 'Home Essentials', 'name': 'Bedsheet (Single)', 'unit': 'piece', 'base_price': 60},
            {'category': 'Home Essentials', 'name': 'Bedsheet (Double)', 'unit': 'piece', 'base_price': 100},
            {'category': 'Home Essentials', 'name': 'Blanket (Single)', 'unit': 'piece', 'base_price': 120},
            {'category': 'Home Essentials', 'name': 'Blanket (Double)', 'unit': 'piece', 'base_price': 180},
            {'category': 'Home Essentials', 'name': 'Curtain (per kg)', 'unit': 'kg', 'base_price': 80},
            {'category': 'Home Essentials', 'name': 'Pillow Cover', 'unit': 'piece', 'base_price': 20},
            {'category': 'Home Essentials', 'name': 'Towel', 'unit': 'piece', 'base_price': 30},
        ]

        services = []
        for data in services_data:
            category = category_map.get(data['category'])
            if not category:
                continue

            service, created = Service.objects.get_or_create(
                category=category,
                name=data['name'],
                defaults={
                    'description': f"Professional {data['category'].lower()} service for {data['name'].lower()}",
                    'unit': data['unit'],
                    'min_quantity': 1,
                    'processing_time_hours': 24 if 'Dry Cleaning' in data['category'] or 'Premium' in data['category'] else 12,
                }
            )

            if created:
                # Create pricing for each zone
                for zone in zones:
                    ServicePricing.objects.create(
                        service=service,
                        zone=zone,
                        price=Decimal(data['base_price']) * zone.price_multiplier,
                        express_price=Decimal(data['base_price']) * zone.price_multiplier * Decimal('1.5'),
                    )

            services.append(service)

        self.stdout.write(f'Created {len(services)} services')
        return services

    def seed_partners(self, users, zones):
        """Create partner businesses"""
        self.stdout.write('Creating partners...')

        partner_users = [u for u in users if u.user_type == 'partner']

        partners_data = [
            {
                'business_name': 'CleanPro Laundry Services',
                'business_type': 'laundry',
                'address_line1': '123 Indiranagar Main Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560038',
                'daily_capacity': 100,
            },
            {
                'business_name': 'Sparkle Wash & Dry',
                'business_type': 'dry_cleaning',
                'address_line1': '456 Koramangala 4th Block',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560034',
                'daily_capacity': 80,
            },
            {
                'business_name': 'Fresh & Clean Laundry',
                'business_type': 'laundry',
                'address_line1': '789 Whitefield Main Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560066',
                'daily_capacity': 120,
            },
            {
                'business_name': 'Premium Laundry Care',
                'business_type': 'premium',
                'address_line1': '321 MG Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001',
                'daily_capacity': 60,
            },
        ]

        partners = []
        for i, data in enumerate(partners_data):
            if i >= len(partner_users):
                break

            partner, created = Partner.objects.get_or_create(
                user=partner_users[i],
                defaults={
                    **data,
                    'pricing_zone': zones[i % len(zones)],
                    'service_radius': 10,
                    'status': 'active',
                    'is_verified': True,
                    'commission_rate': Decimal('15.0'),
                    'latitude': Decimal('12.9716') + Decimal(random.uniform(-0.1, 0.1)),
                    'longitude': Decimal('77.5946') + Decimal(random.uniform(-0.1, 0.1)),
                }
            )

            if created:
                # Set initial statistics
                partner.average_rating = Decimal(random.uniform(4.0, 5.0))
                partner.total_ratings = random.randint(50, 200)
                partner.completed_orders = random.randint(100, 500)
                partner.save()

            partners.append(partner)

        self.stdout.write(f'Created {len(partners)} partners')
        return partners

    def seed_partner_availability(self, partners):
        """Create partner availability schedules"""
        self.stdout.write('Creating partner availability...')

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        count = 0
        for partner in partners:
            for day in days:
                # Most partners work 6 days a week
                if day == 'sunday' and random.random() < 0.5:
                    continue

                PartnerAvailability.objects.get_or_create(
                    partner=partner,
                    day_of_week=day,
                    defaults={
                        'start_time': '09:00:00',
                        'end_time': '21:00:00',
                        'is_available': True,
                    }
                )
                count += 1

        self.stdout.write(f'Created {count} availability records')

    def seed_orders(self, users, services, partners):
        """Create sample orders"""
        self.stdout.write('Creating orders...')

        customer_users = [u for u in users if u.user_type == 'customer']
        statuses = ['pending', 'confirmed', 'picked_up', 'in_progress', 'ready', 'out_for_delivery', 'delivered']

        orders = []
        for i in range(30):  # Create 30 orders
            customer = random.choice(customer_users)
            partner = random.choice(partners)

            # Get customer address
            address = Address.objects.filter(user=customer, is_default=True).first()
            if not address:
                continue

            # Create order
            status = random.choice(statuses)
            created_at = timezone.now() - timedelta(days=random.randint(0, 30))

            order = Order.objects.create(
                user=customer,
                pickup_address=address,
                delivery_address=address,
                status=status,
                payment_status='completed' if status == 'delivered' else 'pending',
                payment_method=random.choice(['razorpay', 'stripe', 'wallet', 'cod']),
                pickup_date=created_at.date(),
                pickup_time_slot='morning',
                delivery_date=(created_at + timedelta(days=2)).date(),
                delivery_time_slot='evening',
                assigned_partner=partner if status != 'pending' else None,
                created_at=created_at,
            )

            # Add order items
            num_items = random.randint(3, 8)
            selected_services = random.sample(list(services), min(num_items, len(services)))

            subtotal = Decimal('0')
            for service in selected_services:
                quantity = random.randint(1, 5)
                # Get pricing for partner's zone
                pricing = ServicePricing.objects.filter(
                    service=service,
                    zone=partner.pricing_zone
                ).first()

                if pricing:
                    unit_price = pricing.price
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
            orders.append(order)

        self.stdout.write(f'Created {len(orders)} orders')
        return orders

    def seed_wallets(self, users):
        """Create wallets for users"""
        self.stdout.write('Creating wallets...')

        customer_users = [u for u in users if u.user_type == 'customer']

        count = 0
        for user in customer_users:
            wallet, created = Wallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': Decimal(random.randint(0, 500)),
                }
            )
            count += 1

        self.stdout.write(f'Created {count} wallets')

    def seed_notification_templates(self):
        """Create notification templates"""
        self.stdout.write('Creating notification templates...')

        templates_data = [
            {
                'name': 'order_confirmed',
                'title': 'Order Confirmed',
                'message': 'Your order #{order_number} has been confirmed. We will pick it up soon!',
                'type': 'order',
            },
            {
                'name': 'order_picked_up',
                'title': 'Order Picked Up',
                'message': 'Your laundry has been picked up. Order #{order_number}',
                'type': 'order',
            },
            {
                'name': 'order_ready',
                'title': 'Order Ready',
                'message': 'Your order #{order_number} is ready for delivery!',
                'type': 'order',
            },
            {
                'name': 'order_delivered',
                'title': 'Order Delivered',
                'message': 'Your order #{order_number} has been delivered. Thank you!',
                'type': 'order',
            },
            {
                'name': 'payment_successful',
                'title': 'Payment Successful',
                'message': 'Payment of ₹{amount} received successfully.',
                'type': 'payment',
            },
        ]

        count = 0
        for data in templates_data:
            NotificationTemplate.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            count += 1

        self.stdout.write(f'Created {count} notification templates')
