from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdminOrReceptionist
from .models import Bill
from .serializers import BillSerializer, BillCreateSerializer, MarkPaidSerializer


class BillViewSet(viewsets.ModelViewSet):
    """
    Generate bills and mark them as paid.

    Visibility:
      - patient: sees only their own bills.
      - admin/receptionist: see and manage all bills.
      - doctor: no access (billing is a front-desk/admin concern).

    Filters: ?patient=<id>&paid=true|false
    """

    queryset = Bill.objects.select_related("patient__user").all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["patient", "paid"]

    def get_serializer_class(self):
        if self.action == "create":
            return BillCreateSerializer
        return BillSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "mark_paid"):
            return [IsAuthenticated(), IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "patient":
            return qs.filter(patient__user=user)
        if user.role == "doctor":
            return qs.none()
        return qs

    @action(detail=True, methods=["patch"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        """PATCH /api/v1/billing/{id}/mark-paid/  Body: { "paid": true }"""
        bill = self.get_object()
        serializer = MarkPaidSerializer(bill, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BillSerializer(bill).data)
