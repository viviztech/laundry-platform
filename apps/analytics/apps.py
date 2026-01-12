from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "apps.analytics"
    verbose_name = "Analytics & Business Intelligence"

    def ready(self):
        """Configure admin visibility for partner launch."""
        from django.contrib import admin
        try:
            from config.admin_config import ENABLE_ANALYTICS_DETAILED

            if not ENABLE_ANALYTICS_DETAILED:
                # Unregister detailed analytics models for partner launch
                # Keep basic dashboard metrics, hide detailed reports
                from .models import (
                    DailyRevenueSummary, PartnerPerformanceMetric,
                    CustomerAnalytics, ReportSchedule, AnalyticsCache
                )
                models_to_hide = [
                    DailyRevenueSummary, PartnerPerformanceMetric,
                    CustomerAnalytics, ReportSchedule, AnalyticsCache
                ]
                for model in models_to_hide:
                    try:
                        admin.site.unregister(model)
                    except admin.sites.NotRegistered:
                        pass
        except ImportError:
            pass
