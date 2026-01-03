"""
Partner-specific order management views.

Provides APIs for partners to manage their assigned orders
through the complete laundry processing workflow.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum, Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Order, OrderItem
from .partner_models import (
    OrderProcessingStage,
    OrderItemProcessing,
    PartnerOrderNote,
    DeliveryProof
)
from .partner_serializers import (
    PartnerOrderListSerializer,
    PartnerOrderDetailSerializer,
    OrderProcessingStageSerializer,
    OrderItemProcessingSerializer,
    PartnerOrderNoteSerializer,
    DeliveryProofSerializer,
    AcceptOrderSerializer,
    RejectOrderSerializer,
    UpdateProcessingStageSerializer,
    UpdateItemProcessingSerializer,
)


class IsPartner(permissions.BasePermission):
    """Permission class to check if user is a partner."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'partner_profile')


@extend_schema_view(
    list=extend_schema(
        summary="List partner's orders",
        description="Get all orders assigned to the authenticated partner.",
    ),
    retrieve=extend_schema(
        summary="Get order details",
        description="Get detailed information about a specific order.",
    ),
)
class PartnerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for partners to manage their orders.

    Partners can view orders assigned to them and perform various
    actions like accepting, updating status, marking stages, etc.
    """
    permission_classes = [IsPartner]

    def get_queryset(self):
        """Get orders assigned to this partner."""
        partner = self.request.user.partner_profile
        queryset = Order.objects.filter(
            assigned_partner=partner
        ).select_related(
            'user', 'pickup_address', 'delivery_address', 'assigned_partner'
        ).prefetch_related(
            'items__service',
            'items__garment',
            'processing_stages',
            'partner_notes'
        )

        # Filter by status
        order_status = self.request.query_params.get('status')
        if order_status:
            queryset = queryset.filter(status=order_status)

        # Filter by date
        pickup_date = self.request.query_params.get('pickup_date')
        if pickup_date:
            queryset = queryset.filter(pickup_date=pickup_date)

        # Filter by processing stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(processing_stages__stage=stage).distinct()

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PartnerOrderListSerializer
        return PartnerOrderDetailSerializer

    @extend_schema(
        summary="Get partner dashboard summary",
        description="Get summary statistics for partner dashboard.",
    )
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get dashboard summary for partner."""
        partner = request.user.partner_profile
        today = timezone.now().date()

        # Get statistics
        stats = {
            'total_orders': Order.objects.filter(assigned_partner=partner).count(),
            'pending_acceptance': Order.objects.filter(
                assigned_partner=partner,
                partner_accepted_at__isnull=True,
                partner_rejected_at__isnull=True
            ).count(),
            'today_pickups': Order.objects.filter(
                assigned_partner=partner,
                pickup_date=today,
                status__in=['confirmed', 'pending']
            ).count(),
            'in_progress': Order.objects.filter(
                assigned_partner=partner,
                status__in=['picked_up', 'in_progress']
            ).count(),
            'ready_for_delivery': Order.objects.filter(
                assigned_partner=partner,
                status='ready'
            ).count(),
            'today_deliveries': Order.objects.filter(
                assigned_partner=partner,
                delivery_date=today,
                status__in=['ready', 'out_for_delivery']
            ).count(),
        }

        # Recent orders
        recent_orders = Order.objects.filter(
            assigned_partner=partner
        ).select_related('user').order_by('-created_at')[:5]

        return Response({
            'statistics': stats,
            'recent_orders': PartnerOrderListSerializer(recent_orders, many=True).data
        })

    @extend_schema(
        summary="Accept order assignment",
        description="Accept an order assigned to the partner.",
        request=AcceptOrderSerializer,
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_order(self, request, pk=None):
        """Accept an order assignment."""
        order = self.get_object()

        # Check if already accepted or rejected
        if order.partner_accepted_at:
            return Response(
                {'error': 'Order already accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.partner_rejected_at:
            return Response(
                {'error': 'Order already rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Accept order
        order.partner_accepted_at = timezone.now()
        order.status = 'confirmed'
        order.save()

        # Create processing stage
        OrderProcessingStage.objects.create(
            order=order,
            stage='accepted',
            stage_category='assignment',
            performed_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )

        # Send notification to customer (via signals)

        return Response({
            'message': 'Order accepted successfully',
            'order': PartnerOrderDetailSerializer(order).data
        })

    @extend_schema(
        summary="Reject order assignment",
        description="Reject an order assigned to the partner.",
        request=RejectOrderSerializer,
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_order(self, request, pk=None):
        """Reject an order assignment."""
        order = self.get_object()

        # Check if already accepted or rejected
        if order.partner_accepted_at:
            return Response(
                {'error': 'Order already accepted, cannot reject'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.partner_rejected_at:
            return Response(
                {'error': 'Order already rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RejectOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Reject order
        order.partner_rejected_at = timezone.now()
        order.partner_rejection_reason = serializer.validated_data['reason']
        order.assigned_partner = None  # Unassign partner
        order.status = 'pending'  # Reset to pending for reassignment
        order.save()

        # Create processing stage
        OrderProcessingStage.objects.create(
            order=order,
            stage='rejected',
            stage_category='assignment',
            performed_by=request.user,
            notes=serializer.validated_data['reason']
        )

        return Response({
            'message': 'Order rejected successfully'
        })

    @extend_schema(
        summary="Update processing stage",
        description="Update the current processing stage of an order.",
        request=UpdateProcessingStageSerializer,
    )
    @action(detail=True, methods=['post'], url_path='update-stage')
    def update_stage(self, request, pk=None):
        """Update processing stage."""
        order = self.get_object()

        serializer = UpdateProcessingStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create new processing stage
        stage_data = serializer.validated_data
        new_stage = OrderProcessingStage.objects.create(
            order=order,
            stage=stage_data['stage'],
            stage_category=self._get_stage_category(stage_data['stage']),
            performed_by=request.user,
            notes=stage_data.get('notes', ''),
            photos=stage_data.get('photos', []),
            has_issue=stage_data.get('has_issue', False),
            issue_description=stage_data.get('issue_description', '')
        )

        # Update order status based on stage
        self._update_order_status_from_stage(order, stage_data['stage'])

        return Response({
            'message': 'Processing stage updated successfully',
            'stage': OrderProcessingStageSerializer(new_stage).data
        })

    @extend_schema(
        summary="Mark order as picked up",
        description="Mark order as picked up from customer.",
    )
    @action(detail=True, methods=['post'], url_path='mark-picked-up')
    def mark_picked_up(self, request, pk=None):
        """Mark order as picked up."""
        order = self.get_object()

        order.status = 'picked_up'
        order.save()

        # Create processing stage
        OrderProcessingStage.objects.create(
            order=order,
            stage='pickup_completed',
            stage_category='pickup',
            performed_by=request.user,
            notes=request.data.get('notes', '')
        )

        # Create item processing records for each item
        for item in order.items.all():
            OrderItemProcessing.objects.get_or_create(
                order_item=item,
                defaults={
                    'status': 'pending',
                    'inspection_at': timezone.now(),
                    'processed_by': request.user
                }
            )

        return Response({
            'message': 'Order marked as picked up',
            'order': PartnerOrderDetailSerializer(order).data
        })

    @extend_schema(
        summary="Update item processing",
        description="Update processing details for a specific order item.",
        request=UpdateItemProcessingSerializer,
    )
    @action(detail=True, methods=['post'], url_path='update-item')
    def update_item_processing(self, request, pk=None):
        """Update item processing details."""
        order = self.get_object()

        serializer = UpdateItemProcessingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        order_item = get_object_or_404(OrderItem, id=data['order_item_id'], order=order)

        # Get or create item processing record
        item_processing, created = OrderItemProcessing.objects.get_or_create(
            order_item=order_item,
            defaults={'processed_by': request.user}
        )

        # Update fields
        item_processing.status = data['status']
        if 'notes' in data:
            item_processing.processing_notes = data['notes']
        if 'has_stains' in data:
            item_processing.has_stains = data['has_stains']
            item_processing.stain_details = data.get('stain_details', '')
        if 'has_damage' in data:
            item_processing.has_damage = data['has_damage']
            item_processing.damage_details = data.get('damage_details', '')
        if 'additional_charges' in data:
            item_processing.additional_charges = data['additional_charges']
            item_processing.additional_charges_reason = data.get('additional_charges_reason', '')

        # Update timestamps based on status
        self._update_item_timestamps(item_processing, data['status'])

        item_processing.save()

        return Response({
            'message': 'Item processing updated successfully',
            'item_processing': OrderItemProcessingSerializer(item_processing).data
        })

    @extend_schema(
        summary="Add partner note",
        description="Add an internal note to the order.",
    )
    @action(detail=True, methods=['post'], url_path='add-note')
    def add_note(self, request, pk=None):
        """Add a partner note to the order."""
        order = self.get_object()

        serializer = PartnerOrderNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = serializer.save(
            order=order,
            created_by=request.user
        )

        return Response({
            'message': 'Note added successfully',
            'note': PartnerOrderNoteSerializer(note).data
        })

    @extend_schema(
        summary="Submit delivery proof",
        description="Submit delivery proof with photos and signature.",
    )
    @action(detail=True, methods=['post'], url_path='delivery-proof')
    def submit_delivery_proof(self, request, pk=None):
        """Submit delivery proof."""
        order = self.get_object()

        serializer = DeliveryProofSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create delivery proof
        proof = serializer.save(
            order=order,
            delivered_by=request.user,
            delivered_at=timezone.now()
        )

        # Update order status
        order.status = 'delivered'
        order.completed_at = timezone.now()
        order.save()

        # Create processing stage
        OrderProcessingStage.objects.create(
            order=order,
            stage='delivered',
            stage_category='delivery',
            performed_by=request.user,
            completed_at=timezone.now()
        )

        return Response({
            'message': 'Delivery proof submitted successfully',
            'proof': DeliveryProofSerializer(proof).data
        })

    def _get_stage_category(self, stage):
        """Get category for a stage."""
        stage_categories = {
            'assigned': 'assignment',
            'accepted': 'assignment',
            'rejected': 'assignment',
            'pickup_scheduled': 'pickup',
            'out_for_pickup': 'pickup',
            'pickup_completed': 'pickup',
            'inspection': 'inspection',
            'inspection_complete': 'inspection',
            'stain_treatment': 'processing',
            'washing': 'processing',
            'drying': 'processing',
            'ironing': 'processing',
            'steam_pressing': 'processing',
            'quality_check': 'finishing',
            'packaging': 'finishing',
            'ready_for_delivery': 'finishing',
            'out_for_delivery': 'delivery',
            'delivered': 'delivery',
            'on_hold': 'issue',
            'issue_reported': 'issue',
        }
        return stage_categories.get(stage, 'processing')

    def _update_order_status_from_stage(self, order, stage):
        """Update order status based on processing stage."""
        status_mapping = {
            'pickup_completed': 'picked_up',
            'washing': 'in_progress',
            'drying': 'in_progress',
            'ironing': 'in_progress',
            'ready_for_delivery': 'ready',
            'out_for_delivery': 'out_for_delivery',
            'delivered': 'delivered',
        }

        if stage in status_mapping:
            order.status = status_mapping[stage]
            order.save()

    def _update_item_timestamps(self, item_processing, item_status):
        """Update timestamps based on item status."""
        now = timezone.now()

        if item_status == 'inspecting':
            item_processing.inspection_at = now
        elif item_status == 'washing':
            if not item_processing.washing_started_at:
                item_processing.washing_started_at = now
        elif item_status == 'drying':
            if item_processing.washing_started_at and not item_processing.washing_completed_at:
                item_processing.washing_completed_at = now
            if not item_processing.drying_started_at:
                item_processing.drying_started_at = now
        elif item_status == 'ironing':
            if item_processing.drying_started_at and not item_processing.drying_completed_at:
                item_processing.drying_completed_at = now
            if not item_processing.ironing_started_at:
                item_processing.ironing_started_at = now
        elif item_status == 'packaged':
            if item_processing.ironing_started_at and not item_processing.ironing_completed_at:
                item_processing.ironing_completed_at = now
        elif item_status == 'completed':
            item_processing.completed_at = now
