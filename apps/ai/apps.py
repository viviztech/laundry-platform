from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "apps.ai"
    verbose_name = "AI & Machine Learning"

    def ready(self):
        """Configure admin visibility for partner launch."""
        from django.contrib import admin
        try:
            from config.admin_config import ENABLE_AI_FEATURES

            if not ENABLE_AI_FEATURES:
                # Unregister AI models from admin for partner launch
                from .models import (
                    GarmentRecognition, PriceEstimation, DemandForecast,
                    Recommendation, FraudDetection, MLModel
                )
                models_to_hide = [
                    GarmentRecognition, PriceEstimation, DemandForecast,
                    Recommendation, FraudDetection, MLModel
                ]
                for model in models_to_hide:
                    try:
                        admin.site.unregister(model)
                    except admin.sites.NotRegistered:
                        pass
        except ImportError:
            pass
