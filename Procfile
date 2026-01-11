# Railway Procfile for LaundryConnect Platform
# This file defines the processes that Railway will run

# Web process - ASGI server for Django with WebSocket support
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application

# Worker process - Celery worker for background tasks
worker: celery -A config worker --loglevel=info --concurrency=2

# Beat process - Celery beat for scheduled tasks
beat: celery -A config beat --loglevel=info
