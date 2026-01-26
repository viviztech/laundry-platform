from django.apps import AppConfig


class TrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "apps.tracking"
    verbose_name = "Location Tracking"

    def ready(self):
        """Configure admin visibility for partner launch."""
        from django.contrib import admin
        try:
            from config.admin_config import ENABLE_LOCATION_TRACKING

            if not ENABLE_LOCATION_TRACKING:
                # Unregister tracking models for partner launch
                # Can be enabled later when real-time tracking is needed
                from .models import LocationUpdate, Route, TrackingSession
                models_to_hide = [LocationUpdate, Route, TrackingSession]
                for model in models_to_hide:
                    try:
                        admin.site.unregister(model)
                    except admin.sites.NotRegistered:
                        pass
        except ImportError:
            pass
