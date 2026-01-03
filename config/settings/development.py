"""
Development settings for LaundryConnect project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

# Add development-specific apps
INSTALLED_APPS += [
    "django_extensions",
    # "debug_toolbar",  # Temporarily disabled due to Python 3.14 compatibility
]

# Debug toolbar middleware
# MIDDLEWARE += [
#     "debug_toolbar.middleware.DebugToolbarMiddleware",
# ]

# Debug toolbar configuration
# INTERNAL_IPS = [
#     "127.0.0.1",
# ]

# CORS settings for development (allow all origins)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email backend for development (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ===== Twilio SMS Configuration =====
# Get credentials from environment or leave empty for testing
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
# Optional: Callback URL for SMS delivery status
TWILIO_STATUS_CALLBACK_URL = config('TWILIO_STATUS_CALLBACK_URL', default='')

# ===== Web Push Notifications (VAPID) =====
# Generate keys with: python manage.py generate_vapid_keys
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY', default='')
VAPID_ADMIN_EMAIL = config('VAPID_ADMIN_EMAIL', default='mailto:admin@laundryconnect.com')

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Show SQL queries
            "propagate": False,
        },
    },
}
