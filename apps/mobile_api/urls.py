"""
Mobile API URLs
"""

from django.urls import path
from . import views

app_name = 'mobile_api'

urlpatterns = [
    # Mobile-optimized endpoints
    path('dashboard/', views.mobile_dashboard, name='dashboard'),
    path('services/', views.mobile_services, name='services'),
    path('orders/', views.mobile_orders, name='orders'),
    path('upload-image/', views.upload_image, name='upload-image'),
    path('stats/', views.user_stats, name='user-stats'),
    path('config/', views.app_config, name='app-config'),
]
