"""
Development settings for LaundryConnect project.
Runs clean Django + PostgreSQL without Redis, Celery or Channels.
"""

from .base import *
import dj_database_url

# Enable debug
DEBUG = True

# Allow all hosts (Docker + local + EC2)
ALLOWED_HOSTS = ["*"]

# Use AWS PostgreSQL via DATABASE_URL
DATABASES['default'] = dj_database_url.config(
    default=config("DATABASE_URL"),
    conn_max_age=600,
)

# CORS - allow all (for mobile & web apps)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email prints to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable Redis / Celery / Channels
CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None
CHANNEL_LAYERS = {}

# Optional Twilio (can be empty)
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER", default="")

# VAPID keys (optional)
VAPID_PRIVATE_KEY = config("VAPID_PRIVATE_KEY", default="")
VAPID_PUBLIC_KEY = config("VAPID_PUBLIC_KEY", default="")
VAPID_ADMIN_EMAIL = config("VAPID_ADMIN_EMAIL", default="mailto:admin@laundryconnect.com")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
