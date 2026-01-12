"""
Base settings for LaundryConnect project.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-temp-key-change-in-production')

# Application definition
DJANGO_APPS = [
    "unfold",  # Modern admin UI - must be before django.contrib.admin
    "daphne",  # Must be first for Channels support
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "channels",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.services",
    "apps.orders",
    "apps.partners",
    "apps.payments",
    "apps.notifications",
    "apps.realtime",
    "apps.chat",
    "apps.tracking",
    "apps.analytics",
    "apps.ai",
    "apps.mobile_api",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ASGI Application for Channels
ASGI_APPLICATION = "config.asgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config('DB_NAME', default='laundry_db'),
        "USER": config('DB_USER', default='postgres'),
        "PASSWORD": config('DB_PASSWORD', default='postgres'),
        "HOST": config('DB_HOST', default='localhost'),
        "PORT": config('DB_PORT', default='5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"  # Indian timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# API Documentation (drf-spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "LaundryConnect API",
    "DESCRIPTION": "On-Demand Laundry Aggregator Platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Redis Configuration
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_DB = config('REDIS_DB', default='0')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "laundry",
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Session Configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Django Channels Configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, int(REDIS_PORT))],
            "capacity": 1500,  # Maximum messages to store
            "expiry": 10,  # Message expiry in seconds
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# ===========================
# Django Unfold Configuration
# ===========================
UNFOLD = {
    "SITE_TITLE": "LaundryConnect Admin",
    "SITE_HEADER": "LaundryConnect Management",
    "SITE_URL": "/",
    "SITE_SYMBOL": "laundry",  # Symbol from icon set
    "SHOW_HISTORY": True,  # Show history on detail pages
    "SHOW_VIEW_ON_SITE": True,  # Show view on site button
    "ENVIRONMENT": "config.settings.base.environment_callback",
    "DASHBOARD_CALLBACK": "config.settings.base.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in sidebar
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,  # Top border
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Core Management",
                "separator": True,
                "items": [
                    {
                        "title": "Users & Accounts",
                        "icon": "people",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "Orders",
                        "icon": "shopping_cart",
                        "link": "/admin/orders/order/",
                    },
                    {
                        "title": "Services",
                        "icon": "local_laundry_service",
                        "link": "/admin/services/service/",
                    },
                    {
                        "title": "Partners",
                        "icon": "business",
                        "link": "/admin/partners/partner/",
                    },
                ],
            },
            {
                "title": "Payments & Finance",
                "separator": True,
                "items": [
                    {
                        "title": "Payments",
                        "icon": "payment",
                        "link": "/admin/payments/payment/",
                    },
                    {
                        "title": "Wallets",
                        "icon": "account_balance_wallet",
                        "link": "/admin/payments/wallet/",
                    },
                ],
            },
            {
                "title": "Analytics & Reports",
                "separator": True,
                "items": [
                    {
                        "title": "Analytics Dashboard",
                        "icon": "analytics",
                        "link": "/admin/analytics/",
                    },
                ],
            },
        ],
    },
}


def environment_callback(request):
    """Return environment badge for admin header."""
    import os
    env = os.getenv('DJANGO_ENV', 'development')

    if env == 'production':
        return ["production", "danger"]  # Red badge
    elif env == 'staging':
        return ["staging", "warning"]  # Yellow badge
    else:
        return ["development", "info"]  # Blue badge


def dashboard_callback(request, context):
    """Custom dashboard with analytics."""
    from django.utils.timezone import now
    from datetime import timedelta
    from apps.orders.models import Order
    from apps.payments.models import Payment
    from apps.partners.models import Partner
    from django.db.models import Sum, Count

    today = now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Calculate metrics
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_week = Order.objects.filter(created_at__date__gte=week_ago).count()
    orders_month = Order.objects.filter(created_at__date__gte=month_ago).count()

    revenue_today = Payment.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    revenue_week = Payment.objects.filter(
        created_at__date__gte=week_ago,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    revenue_month = Payment.objects.filter(
        created_at__date__gte=month_ago,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    active_partners = Partner.objects.filter(status='active', is_verified=True).count()
    pending_orders = Order.objects.filter(status__in=['pending', 'processing']).count()

    # Add to context
    context.update({
        "kpi": [
            {
                "title": "Orders Today",
                "metric": orders_today,
                "footer": f"{orders_week} this week, {orders_month} this month",
            },
            {
                "title": "Revenue Today",
                "metric": f"₹{revenue_today:,.2f}",
                "footer": f"₹{revenue_week:,.2f} this week, ₹{revenue_month:,.2f} this month",
            },
            {
                "title": "Active Partners",
                "metric": active_partners,
                "footer": "Verified and active",
            },
            {
                "title": "Pending Orders",
                "metric": pending_orders,
                "footer": "Requires attention",
            },
        ]
    })

    return context
