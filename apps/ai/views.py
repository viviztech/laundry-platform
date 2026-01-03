"""API views for AI features."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    GarmentRecognition,
    PriceEstimation,
    DemandForecast,
    Recommendation,
    FraudDetection,
    MLModel
)
from .serializers import (
    GarmentRecognitionSerializer,
    PriceEstimationSerializer,
    DemandForecastSerializer,
    RecommendationSerializer,
    FraudDetectionSerializer,
    MLModelSerializer
)
from .services import (
    RecommendationService,
    FraudDetectionService,
    PriceEstimationService,
    DemandForecastService
)


class RecommendationViewSet(viewsets.ModelViewSet):
    """Personalized recommendations API."""
    
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new recommendations for user."""
        service = RecommendationService()
        order_id = request.data.get('order_id')
        order = None
        
        if order_id:
            from apps.orders.models import Order
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                pass
        
        recommendations = service.generate_recommendations(
            user=request.user,
            order=order,
            limit=5
        )
        
        # Save recommendations
        saved_recs = []
        for rec in recommendations:
            rec.save()
            saved_recs.append(rec)
        
        serializer = self.get_serializer(saved_recs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def interact(self, request, pk=None):
        """Track interaction with recommendation."""
        recommendation = self.get_object()
        action_type = request.data.get('action')  # 'shown', 'clicked', 'accepted'
        
        if action_type not in ['shown', 'clicked', 'accepted']:
            return Response(
                {'error': 'Invalid action. Must be: shown, clicked, or accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = RecommendationService()
        service.track_interaction(recommendation, action_type)
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)


class PriceEstimationViewSet(viewsets.ModelViewSet):
    """Price estimation API."""
    
    serializer_class = PriceEstimationSerializer
    permission_classes = [IsAuthenticated]
    queryset = PriceEstimation.objects.all()
    
    @action(detail=False, methods=['post'])
    def estimate(self, request):
        """Get price estimate for a service."""
        garment_type = request.data.get('garment_type')
        service_type = request.data.get('service_type')
        urgency = request.data.get('urgency', 'standard')
        
        if not garment_type or not service_type:
            return Response(
                {'error': 'garment_type and service_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PriceEstimationService()
        estimation = service.estimate_price(
            garment_type=garment_type,
            service_type=service_type,
            urgency=urgency
        )
        
        serializer = self.get_serializer(estimation)
        return Response(serializer.data)


class DemandForecastViewSet(viewsets.ModelViewSet):
    """Demand forecasting API (Admin only)."""
    
    serializer_class = DemandForecastSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = DemandForecast.objects.all()
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate demand forecast."""
        from datetime import datetime
        
        forecast_date_str = request.data.get('forecast_date')
        if not forecast_date_str:
            return Response(
                {'error': 'forecast_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            forecast_date = datetime.strptime(forecast_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = DemandForecastService()
        forecast = service.forecast_demand(forecast_date=forecast_date)
        
        serializer = self.get_serializer(forecast)
        return Response(serializer.data)


class FraudDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Fraud detection API (Admin only)."""
    
    serializer_class = FraudDetectionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = FraudDetection.objects.all()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending fraud reviews."""
        pending = FraudDetection.objects.filter(status='pending').order_by('-risk_score')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Review a fraud case."""
        detection = self.get_object()
        action = request.data.get('action')  # 'approve', 'block'
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            detection.status = 'approved'
        elif action == 'block':
            detection.status = 'blocked'
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        detection.reviewed_by = request.user
        detection.resolution_notes = notes
        detection.save()
        
        serializer = self.get_serializer(detection)
        return Response(serializer.data)


class GarmentRecognitionViewSet(viewsets.ModelViewSet):
    """Garment recognition API."""
    
    serializer_class = GarmentRecognitionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return GarmentRecognition.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def recognize(self, request):
        """Upload image for garment recognition."""
        # Simplified - would integrate with CV API in production
        return Response(
            {'message': 'Garment recognition not yet fully implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class MLModelViewSet(viewsets.ModelViewSet):
    """ML Model management API (Admin only)."""
    
    serializer_class = MLModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MLModel.objects.all()
    
    @action(detail=True, methods=['patch'])
    def deploy(self, request, pk=None):
        """Deploy a model to production."""
        model = self.get_object()
        model.status = 'production'
        from django.utils import timezone
        model.deployed_at = timezone.now()
        model.save()
        
        serializer = self.get_serializer(model)
        return Response(serializer.data)
