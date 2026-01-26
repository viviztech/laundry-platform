"""
API views for orders app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Order, OrderItem, OrderAddon, OrderStatusHistory, OrderRating
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer,
    OrderRatingSerializer,
)
from apps.services.models import Service, Addon
from apps.accounts.models import Address


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an order to view it.
    Admins can view all orders.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user


@extend_schema_view(
    list=extend_schema(
        summary="List orders",
        description="Get all orders for the authenticated user. Admins can see all orders.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by order status'),
            OpenApiParameter(name='payment_status', description='Filter by payment status'),
        ],
    ),
    retrieve=extend_schema(
        summary="Get order",
        description="Get details of a specific order.",
    ),
    create=extend_schema(
        summary="Create order",
        description="Create a new order with items and optional addons.",
        request=CreateOrderSerializer,
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders.
    Users can create and view their own orders.
    Admins can view and manage all orders.
    """
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        """Get orders based on user role."""
        queryset = Order.objects.select_related(
            'user', 'pickup_address', 'delivery_address'
        ).prefetch_related(
            'items__service',
            'addons__addon',
            'status_history',
            'rating'
        )

        # Non-admin users can only see their own orders
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        # Filter by status
        order_status = self.request.query_params.get('status')
        if order_status:
            queryset = queryset.filter(status=order_status)

        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new order with items and addons."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        data = serializer.validated_data

        # Validate addresses belong to user
        try:
            pickup_address = Address.objects.get(
                id=data['pickup_address'],
                user=request.user
            )
        except Address.DoesNotExist:
            return Response(
                {"error": "Invalid pickup address."},
                status=status.HTTP_400_BAD_REQUEST
            )

        delivery_address = None
        if data.get('delivery_address'):
            try:
                delivery_address = Address.objects.get(
                    id=data['delivery_address'],
                    user=request.user
                )
            except Address.DoesNotExist:
                return Response(
                    {"error": "Invalid delivery address."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create order
        order = Order.objects.create(
            user=request.user,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            pickup_date=data['pickup_date'],
            pickup_time_slot=data['pickup_time_slot'],
            delivery_date=data.get('delivery_date'),
            delivery_time_slot=data.get('delivery_time_slot', ''),
            special_instructions=data.get('special_instructions', ''),
            customer_notes=data.get('customer_notes', ''),
            payment_method=data['payment_method'],
            status='pending',
            payment_status='pending',
        )

        # Create order items
        subtotal = 0
        for item_data in data['items']:
            try:
                service = Service.objects.get(
                    id=item_data['service_id'],
                    is_active=True
                )
            except Service.DoesNotExist:
                order.delete()
                return Response(
                    {"error": f"Service {item_data['service_id']} not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get pricing for user's zone (default to A for now)
            pricing = service.pricing.filter(
                zone__zone='A',
                is_active=True
            ).first()

            if not pricing:
                order.delete()
                return Response(
                    {"error": f"Pricing not available for service {service.name}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            unit_price = pricing.discount_price or pricing.base_price
            quantity = item_data['quantity']
            total_price = unit_price * quantity

            order_item = OrderItem.objects.create(
                order=order,
                service=service,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                notes=item_data.get('notes', '')
            )

            subtotal += total_price

            # Create addons for this item if any
            if 'addons' in item_data:
                for addon_data in item_data.get('addons', []):
                    try:
                        addon = Addon.objects.get(
                            id=addon_data['addon_id'],
                            is_active=True
                        )
                    except Addon.DoesNotExist:
                        continue

                    addon_quantity = addon_data.get('quantity', 1)
                    addon_total = addon.price * addon_quantity

                    OrderAddon.objects.create(
                        order=order,
                        order_item=order_item,
                        addon=addon,
                        quantity=addon_quantity,
                        unit_price=addon.price,
                        total_price=addon_total
                    )

                    subtotal += addon_total

        # Handle top-level addons if any
        for addon_data in data.get('addons', []):
            try:
                addon = Addon.objects.get(
                    id=addon_data['addon_id'],
                    is_active=True
                )
            except Addon.DoesNotExist:
                continue

            addon_quantity = addon_data.get('quantity', 1)
            addon_total = addon.price * addon_quantity

            OrderAddon.objects.create(
                order=order,
                addon=addon,
                quantity=addon_quantity,
                unit_price=addon.price,
                total_price=addon_total
            )

            subtotal += addon_total

        # Calculate totals
        tax_amount = subtotal * 0.18  # 18% tax
        delivery_fee = 50  # Fixed delivery fee for now
        total_amount = subtotal + tax_amount + delivery_fee

        # Update order with calculated amounts
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.delivery_fee = delivery_fee
        order.total_amount = total_amount
        order.save()

        # Return created order
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update order status",
        description="Update the status of an order. Creates a status history entry.",
        request=UpdateOrderStatusSerializer,
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, id=None):
        """Update order status."""
        order = self.get_object()

        serializer = UpdateOrderStatusSerializer(
            data=request.data,
            context={'order': order}
        )
        serializer.is_valid(raise_exception=True)

        old_status = order.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        # Update order status
        order.status = new_status

        # Update timestamps
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = timezone.now()
        elif new_status == 'delivered' and not order.completed_at:
            order.completed_at = timezone.now()

        order.save()

        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            notes=notes
        )

        return Response(OrderSerializer(order).data)

    @extend_schema(
        summary="Cancel order",
        description="Cancel an order. Only pending and confirmed orders can be cancelled.",
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, id=None):
        """Cancel an order."""
        order = self.get_object()

        if order.status not in ['pending', 'confirmed']:
            return Response(
                {"error": "Only pending or confirmed orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status
        order.status = 'cancelled'
        order.save()

        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status='cancelled',
            changed_by=request.user,
            notes=request.data.get('notes', 'Order cancelled by user.')
        )

        return Response(OrderSerializer(order).data)

    @extend_schema(
        summary="Rate order",
        description="Add or update rating for a delivered order.",
        request=OrderRatingSerializer,
    )
    @action(detail=True, methods=['post'])
    def rate(self, request, id=None):
        """Rate an order."""
        order = self.get_object()

        if order.status != 'delivered':
            return Response(
                {"error": "Only delivered orders can be rated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if rating already exists
        rating, created = OrderRating.objects.get_or_create(
            order=order,
            user=request.user,
            defaults={
                'service_rating': request.data.get('service_rating'),
                'delivery_rating': request.data.get('delivery_rating'),
                'overall_rating': request.data.get('overall_rating'),
                'review': request.data.get('review', ''),
            }
        )

        if not created:
            # Update existing rating
            serializer = OrderRatingSerializer(rating, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = OrderRatingSerializer(rating)

        return Response(serializer.data)
