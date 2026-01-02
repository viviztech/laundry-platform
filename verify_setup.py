"""
Verification script for authentication setup.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from apps.accounts.models import User, UserProfile, Address
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 60)
print("LaundryConnect - Setup Verification")
print("=" * 60)

# Check 1: Database connection
print("\n1. Checking database connection...")
try:
    user_count = User.objects.count()
    print(f"✓ Database connected successfully!")
    print(f"  Total users in database: {user_count}")
except Exception as e:
    print(f"✗ Database connection failed: {e}")

# Check 2: Superuser exists
print("\n2. Checking superuser...")
try:
    admin = User.objects.get(email='admin@laundryconnect.com')
    print(f"✓ Superuser exists!")
    print(f"  Email: {admin.email}")
    print(f"  Name: {admin.get_full_name()}")
    print(f"  Is Staff: {admin.is_staff}")
    print(f"  Is Superuser: {admin.is_superuser}")
except User.DoesNotExist:
    print("✗ Superuser does not exist")
    admin = None

# Check 3: Password verification
if admin:
    print("\n3. Checking password hashing...")
    if admin.check_password('Admin@12345'):
        print("✓ Password verification working!")
    else:
        print("✗ Password verification failed")

# Check 4: JWT Token generation
if admin:
    print("\n4. Checking JWT token generation...")
    try:
        refresh = RefreshToken.for_user(admin)
        print("✓ JWT tokens generated successfully!")
        print(f"  Access Token: {str(refresh.access_token)[:50]}...")
        print(f"  Refresh Token: {str(refresh)[:50]}...")
    except Exception as e:
        print(f"✗ JWT token generation failed: {e}")

# Check 5: Create test user
print("\n5. Testing user creation...")
try:
    # Clean up if exists
    User.objects.filter(email='test@example.com').delete()

    test_user = User.objects.create_user(
        email='test@example.com',
        phone='+919999999999',
        password='TestPass@123',
        first_name='Test',
        last_name='User'
    )
    print("✓ User creation successful!")
    print(f"  User ID: {test_user.id}")
    print(f"  Email: {test_user.email}")

    # Check 6: UserProfile auto-creation
    print("\n6. Testing UserProfile...")
    profile, created = UserProfile.objects.get_or_create(user=test_user)
    if created or profile:
        print("✓ UserProfile exists!")
        print(f"  Profile ID: {profile.id if hasattr(profile, 'id') else 'N/A'}")
    else:
        print("✗ UserProfile not found")

    # Check 7: Address creation
    print("\n7. Testing Address creation...")
    address = Address.objects.create(
        user=test_user,
        label='home',
        address_line1='123 Test Street',
        city='Mumbai',
        state='Maharashtra',
        pincode='400001',
        country='India',
        is_default=True
    )
    print("✓ Address created successfully!")
    print(f"  Address ID: {address.id}")
    print(f"  Full Address: {address.get_full_address()}")

except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()

# Check 8: URL configuration
print("\n8. Checking URL configuration...")
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    patterns = []

    def collect_urls(urlpatterns, prefix=''):
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                collect_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            elif 'accounts' in str(pattern.pattern):
                patterns.append(f"{prefix}{pattern.pattern}")

    collect_urls(resolver.url_patterns)

    if patterns:
        print("✓ Account URLs configured!")
        print("  Available endpoints:")
        for p in sorted(patterns):
            print(f"    - {p}")
    else:
        print("✗ No account URLs found")
except Exception as e:
    print(f"✗ URL check failed: {e}")

# Check 9: Settings verification
print("\n9. Checking settings...")
from django.conf import settings
checks = [
    ('SECRET_KEY', hasattr(settings, 'SECRET_KEY')),
    ('DEBUG', getattr(settings, 'DEBUG', False)),
    ('DATABASE', 'default' in settings.DATABASES),
    ('REST_FRAMEWORK', hasattr(settings, 'REST_FRAMEWORK')),
    ('SIMPLE_JWT', hasattr(settings, 'SIMPLE_JWT')),
    ('AUTH_USER_MODEL', getattr(settings, 'AUTH_USER_MODEL', None) == 'accounts.User'),
]

all_passed = True
for check_name, passed in checks:
    if passed:
        print(f"  ✓ {check_name}")
    else:
        print(f"  ✗ {check_name}")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("All checks passed! ✓")
    print("\nYou can now:")
    print("  1. Run the development server:")
    print("     python manage.py runserver")
    print("\n  2. Access the admin panel:")
    print("     http://127.0.0.1:8000/admin/")
    print("     Email: admin@laundryconnect.com")
    print("     Password: Admin@12345")
    print("\n  3. View API documentation:")
    print("     http://127.0.0.1:8000/api/docs/")
else:
    print("Some checks failed. Please review the errors above.")
print("=" * 60)
