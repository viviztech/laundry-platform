"""
API views for payments app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction, models
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from decimal import Decimal

from .models import Payment, Wallet, WalletTransaction, Refund, PaymentMethod
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    CreatePaymentSerializer,
    VerifyPaymentSerializer,
    WalletSerializer,
    WalletAddBalanceSerializer,
    WalletTransactionSerializer,
    RefundSerializer,
    RefundListSerializer,
    CreateRefundSerializer,
    ProcessRefundSerializer,
    PaymentMethodSerializer,
    PaymentMethodCreateSerializer,
)
from apps.orders.models import Order

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners to view their own payments/wallet.
    Admins can view all.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        # For Payment, Refund objects
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # For Wallet objects
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


@extend_schema_view(
    list=extend_schema(
        summary="List payments",
        description="Get all payments. Users see only their payments, admins see all.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by payment status'),
            OpenApiParameter(name='method', description='Filter by payment method'),
        ],
    ),
    retrieve=extend_schema(
        summary="Get payment details",
        description="Get details of a specific payment.",
    ),
    create=extend_schema(
        summary="Create payment",
        description="Create a new payment for an order.",
        request=CreatePaymentSerializer,
    ),
)
class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payments.
    Users can view and create their own payments.
    Admins can view and manage all payments.
    """
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        """Get payments based on user role."""
        queryset = Payment.objects.select_related(
            'user', 'order'
        ).prefetch_related('refunds')

        # Non-admin users can only see their own payments
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        # Filter by status
        payment_status = self.request.query_params.get('status')
        if payment_status:
            queryset = queryset.filter(status=payment_status)

        # Filter by payment method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method=method)

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return CreatePaymentSerializer
        return PaymentSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new payment for an order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Get the order
        try:
            order = Order.objects.get(id=data['order_id'])
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify order belongs to user
        if order.user != request.user:
            return Response(
                {"error": "You don't have permission to pay for this order."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if order is already paid
        if order.payment_status == 'paid':
            return Response(
                {"error": "Order is already paid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_amount,
            method=data['method'],
            gateway=data['gateway'],
            status='pending',
        )

        # Here you would typically integrate with payment gateway
        # For now, we'll just return the payment details
        # Gateway integration would create order/payment on gateway side
        # and return gateway_order_id, gateway_payment_id, etc.

        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Verify payment",
        description="Verify a payment after gateway callback.",
        request=VerifyPaymentSerializer,
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def verify(self, request, id=None):
        """Verify payment after gateway callback."""
        payment = self.get_object()

        if payment.status == 'completed':
            return Response(
                {"error": "Payment is already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Here you would verify the payment with the gateway
        # For Razorpay, you'd verify signature
        # For now, we'll mark it as completed

        payment.gateway_payment_id = serializer.validated_data['gateway_payment_id']
        payment.gateway_order_id = serializer.validated_data.get('gateway_order_id', '')
        payment.gateway_signature = serializer.validated_data.get('gateway_signature', '')
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()

        # Update order payment status
        order = payment.order
        order.payment_status = 'paid'
        order.save()

        return Response(PaymentSerializer(payment).data)


@extend_schema_view(
    list=extend_schema(
        summary="List wallets",
        description="Get all wallets. Users see only their wallet, admins see all.",
    ),
    retrieve=extend_schema(
        summary="Get wallet details",
        description="Get details of a specific wallet.",
    ),
)
class WalletViewSet(viewsets.ModelViewSet):
    """
    API endpoint for wallets.
    Users can view and manage their own wallet.
    Admins can view all wallets.
    """
    serializer_class = WalletSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        """Get wallets based on user role."""
        queryset = Wallet.objects.select_related('user').prefetch_related('transactions')

        # Non-admin users can only see their own wallet
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by('-created_at')

    @extend_schema(
        summary="Add balance to wallet",
        description="Add balance to the user's wallet.",
        request=WalletAddBalanceSerializer,
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def add_balance(self, request, id=None):
        """Add balance to wallet."""
        wallet = self.get_object()

        # Only wallet owner or admin can add balance
        if wallet.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to modify this wallet."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = WalletAddBalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Balance added')

        # Add balance to wallet
        wallet.add_balance(amount, description=description)

        return Response(WalletSerializer(wallet).data)

    @extend_schema(
        summary="Get wallet transactions",
        description="Get transaction history for the wallet.",
        parameters=[
            OpenApiParameter(name='transaction_type', description='Filter by transaction type'),
        ],
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, id=None):
        """Get wallet transaction history."""
        wallet = self.get_object()

        transactions = wallet.transactions.all()

        # Filter by transaction type
        transaction_type = request.query_params.get('transaction_type')
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        transactions = transactions.order_by('-created_at')

        # Paginate
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = WalletTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List refunds",
        description="Get all refunds. Users see only their refunds, admins see all.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by refund status'),
        ],
    ),
    retrieve=extend_schema(
        summary="Get refund details",
        description="Get details of a specific refund.",
    ),
    create=extend_schema(
        summary="Request refund",
        description="Request a refund for a payment.",
        request=CreateRefundSerializer,
    ),
)
class RefundViewSet(viewsets.ModelViewSet):
    """
    API endpoint for refunds.
    Users can request and view their own refunds.
    Admins can view and process all refunds.
    """
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        """Get refunds based on user role."""
        queryset = Refund.objects.select_related(
            'payment__order', 'requested_by', 'processed_by'
        )

        # Non-admin users can only see their own refunds
        if not self.request.user.is_staff:
            queryset = queryset.filter(payment__user=self.request.user)

        # Filter by status
        refund_status = self.request.query_params.get('status')
        if refund_status:
            queryset = queryset.filter(status=refund_status)

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return RefundListSerializer
        elif self.action == 'create':
            return CreateRefundSerializer
        return RefundSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Request a new refund."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Get the payment
        payment = Payment.objects.get(id=data['payment_id'])

        # Verify payment belongs to user
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to refund this payment."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create refund request
        refund = Refund.objects.create(
            payment=payment,
            order=payment.order,
            user=request.user,
            amount=data['amount'],
            reason=data['reason'],
            description=data.get('description', ''),
            status='pending',
        )

        response_serializer = RefundSerializer(refund)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Process refund",
        description="Process a refund request. Admin only.",
        request=ProcessRefundSerializer,
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    @transaction.atomic
    def process(self, request, id=None):
        """Process a refund request. Admin only."""
        refund = self.get_object()

        if refund.status not in ['pending', 'processing']:
            return Response(
                {"error": "Refund is already processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProcessRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Update refund status
        refund.status = data['status']
        refund.processed_by = request.user
        refund.processed_at = timezone.now()

        if data.get('gateway_refund_id'):
            refund.gateway_refund_id = data['gateway_refund_id']

        if data.get('error_message'):
            refund.error_message = data['error_message']

        if data['status'] == 'completed':
            refund.completed_at = timezone.now()

            # Update payment status
            payment = refund.payment
            total_refunded = Refund.objects.filter(
                payment=payment,
                status='completed'
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

            if total_refunded >= payment.amount:
                payment.status = 'refunded'
                payment.save()

        refund.save()

        return Response(RefundSerializer(refund).data)


@extend_schema_view(
    list=extend_schema(
        summary="List payment methods",
        description="Get all saved payment methods for the authenticated user.",
    ),
    retrieve=extend_schema(
        summary="Get payment method",
        description="Get details of a specific payment method.",
    ),
    create=extend_schema(
        summary="Add payment method",
        description="Add a new payment method.",
        request=PaymentMethodCreateSerializer,
    ),
)
class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment methods.
    Users can manage their own payment methods.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self):
        """Get payment methods for the authenticated user."""
        return PaymentMethod.objects.filter(
            user=self.request.user
        ).order_by('-is_default', '-created_at')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'create':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Add a new payment method."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Here you would integrate with payment gateway to tokenize card/UPI
        # For now, we'll just create the payment method
        # Gateway integration would save token from gateway

        payment_method = PaymentMethod.objects.create(
            user=request.user,
            type=data['type'],
            provider=data.get('provider', ''),
            nickname=data.get('nickname', ''),
            is_default=data['is_default'],
            card_last4=data.get('card_last4', ''),
            card_brand=data.get('card_brand', ''),
            card_expiry_month=data.get('card_expiry_month'),
            card_expiry_year=data.get('card_expiry_year'),
            upi_id=data.get('upi_id', ''),
            bank_name=data.get('bank_name', ''),
            wallet_provider=data.get('wallet_provider', ''),
            wallet_number=data.get('wallet_number', ''),
            gateway_token='',  # Would be set from gateway integration
        )

        # If set as default, unset others
        if payment_method.is_default:
            PaymentMethod.objects.filter(
                user=request.user,
                is_default=True
            ).exclude(id=payment_method.id).update(is_default=False)

        response_serializer = PaymentMethodSerializer(payment_method)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Set as default",
        description="Set this payment method as default.",
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def set_default(self, request, id=None):
        """Set payment method as default."""
        payment_method = self.get_object()

        # Unset default for other payment methods
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)

        # Set this as default
        payment_method.is_default = True
        payment_method.save()

        return Response(PaymentMethodSerializer(payment_method).data)

    @extend_schema(
        summary="Delete payment method",
        description="Delete a payment method.",
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a payment method."""
        payment_method = self.get_object()

        # Soft delete by marking as inactive
        payment_method.is_active = False
        payment_method.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Update payment method",
        description="Update payment method, primarily for setting as default or updating nickname.",
    )
    def partial_update(self, request, *args, **kwargs):
        """Update payment method (mainly for setting as default or nickname)."""
        instance = self.get_object()

        # If setting as default, handle it with transaction
        if request.data.get('is_default') == True:
            with transaction.atomic():
                # Unset other defaults
                PaymentMethod.objects.filter(
                    user=request.user,
                    is_default=True
                ).exclude(id=instance.id).update(is_default=False)

                instance.is_default = True
                instance.save()

            return Response(PaymentMethodSerializer(instance).data)

        # For other updates (like nickname), use default behavior
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
