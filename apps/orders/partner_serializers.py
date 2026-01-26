"""
Serializers for partner order processing.
"""

from rest_framework import serializers
from django.utils import timezone

from .models import Order, OrderItem
from .partner_models import (
    OrderProcessingStage,
    OrderItemProcessing,
    PartnerOrderNote,
    DeliveryProof
)
from apps.partners.models import Partner


class OrderItemProcessingSerializer(serializers.ModelSerializer):
    """Serializer for item-level processing details."""

    order_item_details = serializers.SerializerMethodField()
    processing_time_hours = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemProcessing
        fields = [
            'id', 'order_item', 'order_item_details', 'status',
            'initial_condition', 'final_condition',
            'has_stains', 'stain_details', 'stain_photos',
            'has_damage', 'damage_details', 'damage_photos',
            'requires_special_care', 'special_care_notes',
            'washing_temp', 'detergent_type', 'drying_method', 'ironing_temp',
            'inspection_at', 'washing_started_at', 'washing_completed_at',
            'drying_started_at', 'drying_completed_at',
            'ironing_started_at', 'ironing_completed_at', 'completed_at',
            'quality_score', 'quality_notes',
            'additional_charges', 'additional_charges_reason',
            'processing_notes', 'processing_time_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_order_item_details(self, obj):
        """Get order item details."""
        return {
            'service_name': obj.order_item.service.name if obj.order_item.service else None,
            'garment_type': obj.order_item.garment.name if obj.order_item.garment else None,
            'quantity': obj.order_item.quantity,
        }

    def get_processing_time_hours(self, obj):
        """Calculate processing time."""
        return obj.calculate_processing_time()


class OrderProcessingStageSerializer(serializers.ModelSerializer):
    """Serializer for processing stages."""

    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    category_display = serializers.CharField(source='get_stage_category_display', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderProcessingStage
        fields = [
            'id', 'order', 'stage', 'stage_display', 'stage_category', 'category_display',
            'performed_by', 'performed_by_name',
            'started_at', 'completed_at', 'duration_minutes',
            'notes', 'photos', 'metadata',
            'has_issue', 'issue_description', 'issue_resolved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_performed_by_name(self, obj):
        """Get performer name."""
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.email
        return None


class PartnerOrderNoteSerializer(serializers.ModelSerializer):
    """Serializer for partner order notes."""

    created_by_name = serializers.SerializerMethodField()
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)

    class Meta:
        model = PartnerOrderNote
        fields = [
            'id', 'order', 'note_type', 'note_type_display', 'content',
            'attachments', 'is_urgent', 'is_resolved',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        """Get creator name."""
        return obj.created_by.get_full_name() or obj.created_by.email


class DeliveryProofSerializer(serializers.ModelSerializer):
    """Serializer for delivery proof."""

    delivered_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryProof
        fields = [
            'id', 'order', 'package_photos', 'delivery_location_photo',
            'customer_signature', 'signature_name',
            'delivered_to', 'delivered_to_relation',
            'delivery_latitude', 'delivery_longitude',
            'delivered_at', 'delivery_notes',
            'delivered_by', 'delivered_by_name',
            'created_at'
        ]
        read_only_fields = ['created_at', 'delivered_by']

    def get_delivered_by_name(self, obj):
        """Get delivery person name."""
        if obj.delivered_by:
            return obj.delivered_by.get_full_name() or obj.delivered_by.email
        return None


class PartnerOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items in partner view."""

    service_name = serializers.CharField(source='service.name', read_only=True)
    garment_name = serializers.CharField(source='garment.name', read_only=True)
    processing_status = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'service_name', 'garment_name', 'quantity',
            'unit_price', 'total_price', 'notes', 'processing_status'
        ]

    def get_processing_status(self, obj):
        """Get processing status if exists."""
        processing = obj.processing_details.first()
        if processing:
            return {
                'status': processing.status,
                'status_display': processing.get_status_display(),
                'has_issues': processing.has_damage or processing.has_stains
            }
        return None


class PartnerOrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for partner order list view."""

    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    current_stage = serializers.SerializerMethodField()
    pickup_address_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'customer_name', 'customer_phone',
            'items_count', 'total_amount',
            'pickup_date', 'pickup_time_slot',
            'delivery_date', 'delivery_time_slot',
            'pickup_address_display',
            'current_stage', 'special_instructions',
            'created_at', 'updated_at'
        ]

    def get_customer_name(self, obj):
        """Get customer name."""
        return obj.user.get_full_name() or obj.user.email

    def get_customer_phone(self, obj):
        """Get customer phone."""
        return obj.user.phone_number

    def get_items_count(self, obj):
        """Count order items."""
        return obj.items.count()

    def get_current_stage(self, obj):
        """Get latest processing stage."""
        latest_stage = obj.processing_stages.order_by('-started_at').first()
        if latest_stage:
            return {
                'stage': latest_stage.stage,
                'stage_display': latest_stage.get_stage_display(),
                'started_at': latest_stage.started_at
            }
        return None

    def get_pickup_address_display(self, obj):
        """Get formatted pickup address."""
        if obj.pickup_address:
            return f"{obj.pickup_address.street_address}, {obj.pickup_address.city}"
        return None


class PartnerOrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for partner order view."""

    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_email = serializers.CharField(source='user.email', read_only=True)

    items = PartnerOrderItemSerializer(many=True, read_only=True)
    processing_stages = OrderProcessingStageSerializer(many=True, read_only=True)
    partner_notes = PartnerOrderNoteSerializer(many=True, read_only=True)
    delivery_proof_data = DeliveryProofSerializer(source='delivery_proof', read_only=True)

    pickup_address_full = serializers.SerializerMethodField()
    delivery_address_full = serializers.SerializerMethodField()

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'customer_name', 'customer_phone', 'customer_email',
            'pickup_address_full', 'delivery_address_full',
            'pickup_date', 'pickup_time_slot',
            'delivery_date', 'delivery_time_slot',
            'items', 'processing_stages', 'partner_notes',
            'delivery_proof_data',
            'subtotal', 'tax_amount', 'delivery_fee', 'total_amount',
            'special_instructions', 'customer_notes', 'internal_notes',
            'partner_accepted_at', 'partner_rejected_at', 'partner_rejection_reason',
            'created_at', 'updated_at', 'confirmed_at', 'completed_at'
        ]

    def get_customer_name(self, obj):
        """Get customer name."""
        return obj.user.get_full_name() or obj.user.email

    def get_customer_phone(self, obj):
        """Get customer phone."""
        return obj.user.phone_number

    def get_pickup_address_full(self, obj):
        """Get full pickup address."""
        if obj.pickup_address:
            return {
                'street': obj.pickup_address.street_address,
                'apartment': obj.pickup_address.apartment,
                'city': obj.pickup_address.city,
                'state': obj.pickup_address.state,
                'pincode': obj.pickup_address.pincode,
                'landmark': obj.pickup_address.landmark,
                'latitude': str(obj.pickup_address.latitude) if obj.pickup_address.latitude else None,
                'longitude': str(obj.pickup_address.longitude) if obj.pickup_address.longitude else None,
            }
        return None

    def get_delivery_address_full(self, obj):
        """Get full delivery address."""
        if obj.delivery_address:
            return {
                'street': obj.delivery_address.street_address,
                'apartment': obj.delivery_address.apartment,
                'city': obj.delivery_address.city,
                'state': obj.delivery_address.state,
                'pincode': obj.delivery_address.pincode,
                'landmark': obj.delivery_address.landmark,
                'latitude': str(obj.delivery_address.latitude) if obj.delivery_address.latitude else None,
                'longitude': str(obj.delivery_address.longitude) if obj.delivery_address.longitude else None,
            }
        return None


class AcceptOrderSerializer(serializers.Serializer):
    """Serializer for accepting an order."""
    estimated_pickup_time = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class RejectOrderSerializer(serializers.Serializer):
    """Serializer for rejecting an order."""
    reason = serializers.CharField(required=True)


class UpdateProcessingStageSerializer(serializers.Serializer):
    """Serializer for updating processing stage."""
    stage = serializers.ChoiceField(choices=OrderProcessingStage.STAGE_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    photos = serializers.ListField(child=serializers.CharField(), required=False)
    has_issue = serializers.BooleanField(required=False, default=False)
    issue_description = serializers.CharField(required=False, allow_blank=True)


class UpdateItemProcessingSerializer(serializers.Serializer):
    """Serializer for updating item processing."""
    order_item_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=OrderItemProcessing.ITEM_STATUS)
    notes = serializers.CharField(required=False, allow_blank=True)
    has_stains = serializers.BooleanField(required=False)
    stain_details = serializers.CharField(required=False, allow_blank=True)
    has_damage = serializers.BooleanField(required=False)
    damage_details = serializers.CharField(required=False, allow_blank=True)
    additional_charges = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    additional_charges_reason = serializers.CharField(required=False, allow_blank=True)
