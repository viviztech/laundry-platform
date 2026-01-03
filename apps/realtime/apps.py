"""
Real-time app configuration.
"""
from django.apps import AppConfig


class RealtimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.realtime'
    verbose_name = 'Real-time Features'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        pass  # No signals needed for realtime app itself
