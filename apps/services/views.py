"""
API views for services app.
"""

from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import ServiceCategory, GarmentType, Service, PricingZone, ServicePricing, Addon
from .serializers import (
    ServiceCategorySerializer,
    GarmentTypeSerializer,
    ServiceSerializer,
    ServiceListSerializer,
    PricingZoneSerializer,
    ServicePricingSerializer,
    AddonSerializer,
    ServiceCatalogSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List service categories",
        description="Get all active service categories.",
    ),
    retrieve=extend_schema(
        summary="Get service category",
        description="Get details of a specific service category.",
    ),
)
class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for service categories.
    Read-only access for customers.
    """
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'


@extend_schema_view(
    list=extend_schema(
        summary="List garment types",
        description="Get all active garment types.",
    ),
    retrieve=extend_schema(
        summary="Get garment type",
        description="Get details of a specific garment type.",
    ),
)
class GarmentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for garment types.
    Read-only access for customers.
    """
    queryset = GarmentType.objects.filter(is_active=True).select_related('category')
    serializer_class = GarmentTypeSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'

    def get_queryset(self):
        """Filter by category if provided."""
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


@extend_schema_view(
    list=extend_schema(
        summary="List services",
        description="Get all active services with pricing information.",
    ),
    retrieve=extend_schema(
        summary="Get service",
        description="Get details of a specific service including pricing for all zones.",
    ),
)
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for services.
    Read-only access for customers.
    """
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'id'

    def get_queryset(self):
        """Filter services with pricing information."""
        queryset = Service.objects.filter(is_active=True).select_related(
            'category', 'garment'
        ).prefetch_related('pricing__zone')

        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by garment
        garment_slug = self.request.query_params.get('garment')
        if garment_slug:
            queryset = queryset.filter(garment__slug=garment_slug)

        # Filter by turnaround time
        turnaround = self.request.query_params.get('turnaround')
        if turnaround:
            queryset = queryset.filter(turnaround_time=turnaround)

        return queryset

    def get_serializer_class(self):
        """Use detailed serializer for retrieve, list serializer for list."""
        if self.action == 'retrieve':
            return ServiceSerializer
        return ServiceListSerializer

    @extend_schema(
        summary="Get pricing for service",
        description="Get pricing information for a specific service in a zone.",
    )
    @action(detail=True, methods=['get'])
    def pricing(self, request, id=None):
        """Get pricing for a specific service."""
        service = self.get_object()
        zone = request.query_params.get('zone', 'A')

        try:
            pricing = ServicePricing.objects.get(
                service=service,
                zone=zone,
                is_active=True
            )
            serializer = ServicePricingSerializer(pricing)
            return Response(serializer.data)
        except ServicePricing.DoesNotExist:
            return Response(
                {"error": "Pricing not available for this zone."},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List pricing zones",
        description="Get all pricing zones.",
    ),
    retrieve=extend_schema(
        summary="Get pricing zone",
        description="Get details of a specific pricing zone.",
    ),
)
class PricingZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for pricing zones.
    Read-only access for customers.
    """
    queryset = PricingZone.objects.all()
    serializer_class = PricingZoneSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'zone'


@extend_schema_view(
    list=extend_schema(
        summary="List add-ons",
        description="Get all active add-on services.",
    ),
    retrieve=extend_schema(
        summary="Get add-on",
        description="Get details of a specific add-on service.",
    ),
)
class AddonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for add-on services.
    Read-only access for customers.
    """
    queryset = Addon.objects.filter(is_active=True)
    serializer_class = AddonSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'


@extend_schema(
    summary="Get complete service catalog",
    description="Get the complete service catalog including categories, garments, services, addons, and zones.",
)
class ServiceCatalogView(generics.GenericAPIView):
    """
    API endpoint to get the complete service catalog.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = ServiceCatalogSerializer

    def get(self, request):
        """Return complete catalog."""
        data = {
            'categories': ServiceCategory.objects.filter(is_active=True),
            'garments': GarmentType.objects.filter(is_active=True).select_related('category'),
            'services': Service.objects.filter(is_active=True).select_related('category', 'garment'),
            'addons': Addon.objects.filter(is_active=True),
            'zones': PricingZone.objects.all(),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
