"""
Mobile-Optimized API Views
Provides lightweight, optimized endpoints for mobile app
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

from apps.accounts.serializers import UserSerializer
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer
from apps.payments.models import Wallet
from apps.notifications.models import Notification
from apps.services.models import ServiceCategory, ServiceItem
from apps.services.serializers import ServiceCategorySerializer, ServiceItemSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_dashboard(request):
    """
    Mobile-optimized dashboard endpoint
    Returns all data needed for home screen in a single request
    """
    user = request.user

    # Get active orders (not delivered or cancelled)
    active_orders = Order.objects.filter(
        user=user,
        status__in=['pending', 'confirmed', 'picked_up', 'in_progress', 'ready', 'out_for_delivery']
    ).order_by('-created_at')[:3]

    # Get recent orders
    recent_orders = Order.objects.filter(
        user=user
    ).order_by('-created_at')[:5]

    # Get wallet balance
    wallet_balance = 0
    try:
        wallet = Wallet.objects.get(user=user)
        wallet_balance = float(wallet.balance)
    except Wallet.DoesNotExist:
        pass

    # Get unread notifications count
    unread_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).count()

    # Get service categories (active only)
    categories = ServiceCategory.objects.filter(
        is_active=True
    ).order_by('display_order')[:6]

    return Response({
        'user': UserSerializer(user).data,
        'active_orders_count': active_orders.count(),
        'active_orders': OrderSerializer(active_orders, many=True).data,
        'recent_orders': OrderSerializer(recent_orders, many=True).data,
        'wallet_balance': wallet_balance,
        'unread_notifications': unread_notifications,
        'service_categories': ServiceCategorySerializer(categories, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_services(request):
    """
    Mobile-optimized services endpoint
    Returns filtered and paginated services
    """
    category_id = request.GET.get('category')

    # Base query
    items = ServiceItem.objects.filter(is_active=True)

    # Filter by category if provided
    if category_id:
        items = items.filter(category_id=category_id)

    # Order by name
    items = items.order_by('name')

    # Limit results for mobile
    limit = int(request.GET.get('limit', 20))
    items = items[:limit]

    return Response({
        'items': ServiceItemSerializer(items, many=True).data,
        'count': items.count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_orders(request):
    """
    Mobile-optimized orders endpoint
    Returns user's orders with optional status filter
    """
    user = request.user
    order_status = request.GET.get('status')

    # Base query
    orders = Order.objects.filter(user=user)

    # Filter by status if provided
    if order_status:
        orders = orders.filter(status=order_status)

    # Order by created date (newest first)
    orders = orders.order_by('-created_at')

    # Limit results
    limit = int(request.GET.get('limit', 50))
    orders = orders[:limit]

    return Response({
        'orders': OrderSerializer(orders, many=True).data,
        'count': orders.count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Handle image uploads from mobile with compression
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    image = request.FILES['image']

    # Validate file size (max 5MB)
    if image.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'Image size must be less than 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if image.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid image format. Allowed: JPEG, PNG, WebP'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: Process and store image
    # For now, return success
    return Response({
        'success': True,
        'message': 'Image uploaded successfully',
        'url': None  # Will be populated after processing
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """
    Get user statistics for profile screen
    """
    user = request.user

    # Calculate stats
    total_orders = Order.objects.filter(user=user).count()
    completed_orders = Order.objects.filter(user=user, status='delivered').count()
    total_spent = Order.objects.filter(
        user=user,
        status='delivered'
    ).aggregate(total=Sum('total'))['total'] or 0

    # Calculate savings (if applicable)
    savings = 0  # TODO: Calculate from discounts/coupons used

    return Response({
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_spent': float(total_spent),
        'savings': savings,
        'member_since': user.created_at.strftime('%B %Y'),
    })


@api_view(['GET'])
def app_config(request):
    """
    Get mobile app configuration
    No authentication required
    """
    return Response({
        'app_version': '1.0.0',
        'min_supported_version': '1.0.0',
        'force_update': False,
        'maintenance_mode': False,
        'features': {
            'chat_enabled': True,
            'tracking_enabled': True,
            'wallet_enabled': True,
            'ai_recognition': True,
        },
        'payment_methods': ['razorpay', 'stripe', 'wallet'],
        'supported_currencies': ['INR'],
    })
