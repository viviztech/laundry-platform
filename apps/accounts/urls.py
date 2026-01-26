"""
URL configuration for accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    AddressListCreateView,
    AddressDetailView,
    RegisterFCMTokenView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Push Notifications
    path('notification-token/', RegisterFCMTokenView.as_view(), name='register_fcm_token'),

    # Addresses
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<uuid:pk>/', AddressDetailView.as_view(), name='address_detail'),
]
