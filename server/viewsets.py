from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Expert, Request, ExpertMatch
from .serializers import (
    CategorySerializer, ExpertSerializer, RequestListSerializer,
    RequestDetailSerializer, RequestCreateSerializer, ExpertMatchSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List categories for request submission"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ExpertViewSet(viewsets.ReadOnlyModelViewSet):
    """Expert directory"""
    queryset = Expert.objects.all()
    serializer_class = ExpertSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__first_name', 'user__last_name', 'expertise']
    ordering_fields = ['help_provided', 'created_at']
    ordering = ['-help_provided']
    filterset_fields = ['availability']


class RequestViewSet(viewsets.ModelViewSet):
    """
    Manage community help requests
    - Public endpoint for submitting new requests
    - Admin endpoint for reviewing and managing
    """
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'requester_name']
    ordering_fields = ['priority', 'created_at', 'value_score']
    ordering = ['-created_at']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        """Get requests, filter by permissions"""
        queryset = Request.objects.all()
        # Optionally filter non-admin users to see only their own requests
        return queryset

    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'create':
            return RequestCreateSerializer
        elif self.action == 'retrieve':
            return RequestDetailSerializer
        return RequestListSerializer

    @action(detail=True, methods=['post'])
    def assign_expert(self, request, pk=None):
        """Assign expert to request (admin only)"""
        req = self.get_object()
        expert_id = request.data.get('expert_id')

        try:
            expert = Expert.objects.get(id=expert_id)
            req.assign_expert(expert)
            return Response({
                'status': 'success',
                'message': f'Expert {expert} assigned to request'
            })
        except Expert.DoesNotExist:
            return Response(
                {'error': 'Expert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark request as resolved"""
        req = self.get_object()
        notes = request.data.get('notes', '')
        req.resolve(notes)
        return Response({
            'status': 'success',
            'message': 'Request marked as resolved'
        })

    @action(detail=True, methods=['get'])
    def suggested_experts(self, request, pk=None):
        """Get AI-suggested expert matches for request"""
        req = self.get_object()
        matches = req.expert_matches.all().order_by('-match_score')[:5]
        serializer = ExpertMatchSerializer(matches, many=True)
        return Response(serializer.data)


class ExpertMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """View expert-request matches"""
    queryset = ExpertMatch.objects.all()
    serializer_class = ExpertMatchSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['match_score', 'created_at']
    ordering = ['-match_score']
    filterset_fields = ['request', 'expert']
