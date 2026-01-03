"""
URL configuration for LaundryConnect platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # API Endpoints
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/partners/", include("apps.partners.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/realtime/", include("apps.realtime.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/mobile/", include("apps.mobile_api.urls")),
    path("api/", include("apps.orders.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar - Temporarily disabled due to Python 3.14 compatibility
    # try:
    #     import debug_toolbar
    #     urlpatterns = [
    #         path('__debug__/', include('debug_toolbar.urls')),
    #     ] + urlpatterns
    # except ImportError:
    #     pass
