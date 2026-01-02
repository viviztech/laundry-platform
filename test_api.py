"""
Simple script to test authentication APIs.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from django.test import Client
from apps.accounts.models import User
import json

client = Client()

print("=" * 60)
print("Testing Authentication APIs")
print("=" * 60)

# Test 1: Register a new user
print("\n1. Testing Registration API...")
register_data = {
    "email": "testuser@example.com",
    "phone": "+919999999999",
    "password": "TestPass@123",
    "password2": "TestPass@123",
    "first_name": "Test",
    "last_name": "User"
}

# Clean up if user already exists
User.objects.filter(email=register_data['email']).delete()

response = client.post('/api/accounts/auth/register/',
                       data=json.dumps(register_data),
                       content_type='application/json')

print(f"Status Code: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print("✓ Registration successful!")
    print(f"  User ID: {data['user']['id']}")
    print(f"  Email: {data['user']['email']}")
    print(f"  Access Token: {data['access'][:30]}...")
    print(f"  Refresh Token: {data['refresh'][:30]}...")
    refresh_token = data['refresh']
else:
    print(f"✗ Registration failed: {response.json()}")
    refresh_token = None

# Test 2: Login
print("\n2. Testing Login API...")
login_data = {
    "email": "admin@laundryconnect.com",
    "password": "Admin@12345"
}

response = client.post('/api/accounts/auth/login/',
                      data=json.dumps(login_data),
                      content_type='application/json')

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("✓ Login successful!")
    print(f"  Email: {data['user']['email']}")
    print(f"  Access Token: {data['access'][:30]}...")
    access_token = data['access']
else:
    print(f"✗ Login failed: {response.json()}")
    access_token = None

# Test 3: Get current user
if access_token:
    print("\n3. Testing Current User API...")
    response = client.get('/api/accounts/me/',
                         HTTP_AUTHORIZATION=f'Bearer {access_token}')

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✓ Current user retrieved successfully!")
        print(f"  Email: {data['email']}")
        print(f"  Name: {data['first_name']} {data['last_name']}")
        print(f"  User Type: {data['user_type']}")
    else:
        print(f"✗ Failed to get current user: {response.content}")

# Test 4: Token Refresh
if refresh_token:
    print("\n4. Testing Token Refresh API...")
    response = client.post('/api/accounts/auth/token/refresh/',
                          data=json.dumps({'refresh': refresh_token}),
                          content_type='application/json')

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✓ Token refresh successful!")
        print(f"  New Access Token: {data['access'][:30]}...")
    else:
        print(f"✗ Token refresh failed: {response.content}")

# Test 5: Create Address
if access_token:
    print("\n5. Testing Create Address API...")
    address_data = {
        "label": "home",
        "address_line1": "123 Main Street",
        "address_line2": "Apt 4B",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "country": "India",
        "contact_name": "Test User",
        "contact_phone": "+919999999999",
        "is_default": True
    }

    response = client.post('/api/accounts/addresses/',
                          data=json.dumps(address_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {access_token}')

    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✓ Address created successfully!")
        print(f"  Address ID: {data['id']}")
        print(f"  Label: {data['label']}")
        print(f"  City: {data['city']}, {data['state']}")
    else:
        print(f"✗ Address creation failed: {response.json()}")

print("\n" + "=" * 60)
print("API Testing Complete!")
print("=" * 60)
