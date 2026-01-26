"""
API views for partners app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Partner, PartnerServiceArea, PartnerAvailability, PartnerHoliday, PartnerPerformance
from .serializers import (
    PartnerSerializer,
    PartnerListSerializer,
    PartnerRegistrationSerializer,
    UpdatePartnerStatusSerializer,
    PartnerVerificationSerializer,
    PartnerServiceAreaSerializer,
    PartnerAvailabilitySerializer,
    PartnerHolidaySerializer,
    PartnerPerformanceSerializer,
)

User = get_user_model()


class IsPartnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow partners to view their own profile.
    Admins can view all partners.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return hasattr(request.user, 'partner_profile') and obj == request.user.partner_profile


@extend_schema_view(
    list=extend_schema(
        summary="List partners",
        description="Get all partners. Admins see all, partners see only themselves.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by partner status'),
            OpenApiParameter(name='city', description='Filter by city'),
            OpenApiParameter(name='is_verified', description='Filter by verification status'),
        ],
    ),
    retrieve=extend_schema(
        summary="Get partner",
        description="Get details of a specific partner.",
    ),
    create=extend_schema(
        summary="Register partner",
        description="Register a new partner. Creates user account and partner profile.",
        request=PartnerRegistrationSerializer,
    ),
)
class PartnerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for partners.
    Partners can view and update their own profile.
    Admins can view and manage all partners.
    """
    permission_classes = (permissions.IsAuthenticated, IsPartnerOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        """Get partners based on user role."""
        queryset = Partner.objects.select_related(
            'user', 'pricing_zone', 'verified_by'
        ).prefetch_related(
            'service_areas', 'availability', 'holidays'
        )

        # Non-admin users can only see their own profile
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'partner_profile'):
                queryset = queryset.filter(user=self.request.user)
            else:
                queryset = queryset.none()

        # Filter by status
        partner_status = self.request.query_params.get('status')
        if partner_status:
            queryset = queryset.filter(status=partner_status)

        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        # Filter by verification
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return PartnerListSerializer
        elif self.action == 'create':
            return PartnerRegistrationSerializer
        return PartnerSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Register a new partner with user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Create user account
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            user_type='partner'
        )

        # Create partner profile
        partner = Partner.objects.create(
            user=user,
            business_name=data['business_name'],
            business_type=data['business_type'],
            business_registration_number=data.get('business_registration_number', ''),
            tax_id=data.get('tax_id', ''),
            contact_person=data['contact_person'],
            contact_email=data['contact_email'],
            contact_phone=data['contact_phone'],
            alternate_phone=data.get('alternate_phone', ''),
            address_line1=data['address_line1'],
            address_line2=data.get('address_line2', ''),
            city=data['city'],
            state=data['state'],
            pincode=data['pincode'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            service_radius=data.get('service_radius', 5.0),
            daily_capacity=data.get('daily_capacity', 50),
            description=data.get('description', ''),
            status='pending',
        )

        # Return created partner
        response_serializer = PartnerSerializer(partner)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update partner status",
        description="Update the status of a partner. Admin only.",
        request=UpdatePartnerStatusSerializer,
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, id=None):
        """Update partner status. Admin only."""
        partner = self.get_object()

        serializer = UpdatePartnerStatusSerializer(
            data=request.data,
            context={'partner': partner}
        )
        serializer.is_valid(raise_exception=True)

        old_status = partner.status
        new_status = serializer.validated_data['status']

        # Update partner status
        partner.status = new_status

        # If activating for the first time, set onboarded_at
        if new_status == 'active' and not partner.onboarded_at:
            partner.onboarded_at = timezone.now()

        partner.save()

        return Response(PartnerSerializer(partner).data)

    @extend_schema(
        summary="Verify partner",
        description="Verify or unverify a partner. Admin only.",
        request=PartnerVerificationSerializer,
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, id=None):
        """Verify or unverify a partner. Admin only."""
        partner = self.get_object()

        serializer = PartnerVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_verified = serializer.validated_data['is_verified']

        partner.is_verified = is_verified
        if is_verified:
            partner.verified_at = timezone.now()
            partner.verified_by = request.user
        else:
            partner.verified_at = None
            partner.verified_by = None

        partner.save()

        return Response(PartnerSerializer(partner).data)

    @extend_schema(
        summary="Get partner performance",
        description="Get performance metrics for a partner.",
    )
    @action(detail=True, methods=['get'])
    def performance(self, request, id=None):
        """Get partner performance metrics."""
        partner = self.get_object()

        # Get query parameters
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        metrics = partner.performance_metrics.all()

        if year:
            metrics = metrics.filter(year=int(year))
        if month:
            metrics = metrics.filter(month=int(month))

        serializer = PartnerPerformanceSerializer(metrics, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get available partners",
        description="Get partners available for new orders in a specific area.",
        parameters=[
            OpenApiParameter(name='pincode', description='Pincode to search', required=True),
        ],
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def available(self, request):
        """Get partners available for new orders in a specific area."""
        pincode = request.query_params.get('pincode')

        if not pincode:
            return Response(
                {"error": "Pincode is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find partners serving this pincode
        partners = Partner.objects.filter(
            service_areas__pincode=pincode,
            service_areas__is_active=True,
            status='active',
            is_verified=True
        ).filter(
            current_load__lt=F('daily_capacity')
        ).select_related('pricing_zone').distinct()

        serializer = PartnerListSerializer(partners, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List partner service areas",
        description="Get service areas for the authenticated partner.",
    ),
    create=extend_schema(
        summary="Add service area",
        description="Add a new service area for the authenticated partner.",
    ),
)
class PartnerServiceAreaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for partner service areas.
    Partners can manage their own service areas.
    """
    serializer_class = PartnerServiceAreaSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self):
        """Get service areas for the authenticated partner."""
        if hasattr(self.request.user, 'partner_profile'):
            return PartnerServiceArea.objects.filter(
                partner=self.request.user.partner_profile
            ).order_by('city', 'pincode')
        return PartnerServiceArea.objects.none()

    def perform_create(self, serializer):
        """Set partner to authenticated user's partner profile."""
        serializer.save(partner=self.request.user.partner_profile)


@extend_schema_view(
    list=extend_schema(
        summary="List partner availability",
        description="Get availability schedule for the authenticated partner.",
    ),
    create=extend_schema(
        summary="Set availability",
        description="Set availability for a specific weekday.",
    ),
)
class PartnerAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for partner availability.
    Partners can manage their own availability schedule.
    """
    serializer_class = PartnerAvailabilitySerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self):
        """Get availability for the authenticated partner."""
        if hasattr(self.request.user, 'partner_profile'):
            return PartnerAvailability.objects.filter(
                partner=self.request.user.partner_profile
            ).order_by('weekday', 'start_time')
        return PartnerAvailability.objects.none()

    def perform_create(self, serializer):
        """Set partner to authenticated user's partner profile."""
        serializer.save(partner=self.request.user.partner_profile)


@extend_schema_view(
    list=extend_schema(
        summary="List partner holidays",
        description="Get holidays for the authenticated partner.",
    ),
    create=extend_schema(
        summary="Add holiday",
        description="Add a holiday for the authenticated partner.",
    ),
)
class PartnerHolidayViewSet(viewsets.ModelViewSet):
    """
    API endpoint for partner holidays.
    Partners can manage their own holidays.
    """
    serializer_class = PartnerHolidaySerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self):
        """Get holidays for the authenticated partner."""
        if hasattr(self.request.user, 'partner_profile'):
            return PartnerHoliday.objects.filter(
                partner=self.request.user.partner_profile
            ).order_by('date')
        return PartnerHoliday.objects.none()

    def perform_create(self, serializer):
        """Set partner to authenticated user's partner profile."""
        serializer.save(partner=self.request.user.partner_profile)
