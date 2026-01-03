"""
REST API views for Location Tracking functionality.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import LocationUpdate, Route, TrackingSession
from .serializers import (
    LocationUpdateSerializer,
    LocationUpdateCreateSerializer,
    RouteSerializer,
    TrackingSessionSerializer,
    GeoJSONSerializer,
)
from apps.orders.models import Order
from apps.partners.models import Partner


class LocationUpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing location updates.

    Endpoints:
    - GET /tracking/locations/ - List location updates
    - POST /tracking/locations/ - Submit location update (partner only)
    - GET /tracking/locations/{id}/ - Get location update details
    - GET /tracking/locations/order/{order_id}/ - Get locations for order
    """

    serializer_class = LocationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get location updates accessible to user."""
        user = self.request.user

        # Partners see their own location updates
        try:
            partner = Partner.objects.get(user=user)
            return LocationUpdate.objects.filter(partner=partner).select_related(
                'order', 'partner'
            )
        except Partner.DoesNotExist:
            # Customers see locations for their orders
            return LocationUpdate.objects.filter(
                order__customer=user
            ).select_related('order', 'partner')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return LocationUpdateCreateSerializer
        return LocationUpdateSerializer

    def create(self, request, *args, **kwargs):
        """Create a new location update (partners only)."""
        # Verify user is a partner
        try:
            partner = Partner.objects.get(user=request.user)
        except Partner.DoesNotExist:
            return Response(
                {'error': 'Only partners can submit location updates.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location_update = serializer.save()

        # Update route ETA if exists
        try:
            route = Route.objects.get(order=location_update.order, is_active=True)
            if location_update.speed:
                route.update_eta(
                    float(location_update.latitude),
                    float(location_update.longitude),
                    location_update.speed
                )
        except Route.DoesNotExist:
            pass

        response_serializer = LocationUpdateSerializer(location_update)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """Get all location updates for a specific order."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locations = LocationUpdate.objects.filter(order=order).select_related(
            'partner'
        ).order_by('-timestamp')

        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)/latest')
    def latest_for_order(self, request, order_id=None):
        """Get the latest location update for an order."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        location = LocationUpdate.objects.filter(order=order).select_related(
            'partner'
        ).first()

        if not location:
            return Response(
                {'error': 'No location updates found for this order.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(location)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)/geojson')
    def geojson_for_order(self, request, order_id=None):
        """Get location updates for an order in GeoJSON format."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locations = LocationUpdate.objects.filter(order=order).order_by('timestamp')

        geojson = {
            'type': 'FeatureCollection',
            'features': [loc.to_geojson() for loc in locations]
        }

        return Response(geojson)


class RouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing delivery routes.

    Endpoints:
    - GET /tracking/routes/ - List routes
    - POST /tracking/routes/ - Create route
    - GET /tracking/routes/{id}/ - Get route details
    - POST /tracking/routes/{id}/start/ - Start route
    - POST /tracking/routes/{id}/complete/ - Complete route
    - GET /tracking/routes/order/{order_id}/ - Get route for order
    """

    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get routes accessible to user."""
        user = self.request.user

        # Partners see their routes
        try:
            partner = Partner.objects.get(user=user)
            return Route.objects.filter(partner=partner).select_related('order', 'partner')
        except Partner.DoesNotExist:
            # Customers see routes for their orders
            return Route.objects.filter(order__customer=user).select_related('order', 'partner')

    @action(detail=True, methods=['post'], url_path='start')
    def start_route(self, request, pk=None):
        """Start a delivery route."""
        route = self.get_object()

        # Verify user is the assigned partner
        try:
            partner = Partner.objects.get(user=request.user)
            if route.partner != partner:
                return Response(
                    {'error': 'You are not assigned to this route.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Partner.DoesNotExist:
            return Response(
                {'error': 'Only partners can start routes.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if route.started_at:
            return Response(
                {'error': 'Route has already been started.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        route.started_at = timezone.now()
        route.is_active = True
        route.save(update_fields=['started_at', 'is_active'])

        # Create tracking session
        TrackingSession.objects.create(
            order=route.order,
            partner=route.partner
        )

        serializer = self.get_serializer(route)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_route(self, request, pk=None):
        """Complete a delivery route."""
        route = self.get_object()

        # Verify user is the assigned partner
        try:
            partner = Partner.objects.get(user=request.user)
            if route.partner != partner:
                return Response(
                    {'error': 'You are not assigned to this route.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Partner.DoesNotExist:
            return Response(
                {'error': 'Only partners can complete routes.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if route.completed_at:
            return Response(
                {'error': 'Route has already been completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        route.completed_at = timezone.now()
        route.actual_arrival = timezone.now()
        route.is_active = False
        route.save(update_fields=['completed_at', 'actual_arrival', 'is_active'])

        # End tracking session
        session = TrackingSession.objects.filter(
            order=route.order,
            partner=route.partner,
            is_active=True
        ).first()

        if session:
            session.end_session()

        serializer = self.get_serializer(route)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """Get route for a specific order."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            route = Route.objects.get(order=order)
            serializer = self.get_serializer(route)
            return Response(serializer.data)
        except Route.DoesNotExist:
            return Response(
                {'error': 'No route found for this order.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='geojson')
    def geojson(self, request, pk=None):
        """Get route in GeoJSON format."""
        route = self.get_object()
        return Response(route.to_geojson())


class TrackingSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing tracking sessions.

    Endpoints:
    - GET /tracking/sessions/ - List sessions
    - GET /tracking/sessions/{id}/ - Get session details
    - GET /tracking/sessions/order/{order_id}/ - Get sessions for order
    """

    serializer_class = TrackingSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get tracking sessions accessible to user."""
        user = self.request.user

        # Partners see their sessions
        try:
            partner = Partner.objects.get(user=user)
            return TrackingSession.objects.filter(partner=partner).select_related(
                'order', 'partner'
            )
        except Partner.DoesNotExist:
            # Customers see sessions for their orders
            return TrackingSession.objects.filter(
                order__customer=user
            ).select_related('order', 'partner')

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """Get all tracking sessions for a specific order."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        sessions = TrackingSession.objects.filter(order=order).select_related('partner')
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)/active')
    def active_for_order(self, request, order_id=None):
        """Get the active tracking session for an order."""
        order = get_object_or_404(Order, id=order_id)

        # Verify access
        if not (order.customer == request.user or
                (hasattr(order, 'assigned_partner') and
                 order.assigned_partner and
                 order.assigned_partner.user == request.user)):
            return Response(
                {'error': 'You do not have access to this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        session = TrackingSession.objects.filter(
            order=order,
            is_active=True
        ).select_related('partner').first()

        if not session:
            return Response(
                {'error': 'No active tracking session for this order.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(session)
        return Response(serializer.data)
