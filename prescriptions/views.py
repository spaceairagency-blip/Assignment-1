from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdminOrDoctor
from .models import Prescription
from .serializers import PrescriptionSerializer, PrescriptionCreateSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Create prescriptions with multiple medicines, and view prescriptions.

    Visibility:
      - patient: sees only prescriptions tied to their own appointments.
      - doctor: sees only prescriptions they wrote.
      - admin/receptionist: see all.

    Only doctors (or admin, for corrections) can create/update/delete
    prescriptions.
    """

    queryset = Prescription.objects.select_related(
        "appointment__patient__user", "appointment__doctor__user"
    ).prefetch_related("prescription_medicines__medicine")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["appointment"]

    def get_serializer_class(self):
        if self.action == "create":
            return PrescriptionCreateSerializer
        return PrescriptionSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "patient":
            return qs.filter(appointment__patient__user=user)
        if user.role == "doctor":
            return qs.filter(appointment__doctor__user=user)
        return qs

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.role == "doctor" and instance.appointment.doctor.user_id != user.id:
            return Response(
                {"detail": "You can only edit your own prescriptions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.role == "doctor" and instance.appointment.doctor.user_id != user.id:
            return Response(
                {"detail": "You can only delete your own prescriptions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
