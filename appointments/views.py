from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import AppointmentFilter
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentStatusUpdateSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Book / View / Update / Cancel appointments.

    Visibility rules:
      - patient: sees only their own appointments.
      - doctor: sees only appointments booked with them.
      - admin/receptionist: see all appointments.

    Filters: ?doctor=<id>&patient=<id>&status=pending&date=YYYY-MM-DD
             &date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    """

    queryset = Appointment.objects.select_related(
        "patient__user", "doctor__user", "doctor__department"
    ).all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    ordering_fields = ["appointment_date", "created_at"]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return AppointmentCreateSerializer
        if self.action in ("update_status",):
            return AppointmentStatusUpdateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "patient":
            return qs.filter(patient__user=user)
        if user.role == "doctor":
            return qs.filter(doctor__user=user)
        return qs  # admin, receptionist see everything

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # Patients may only modify (e.g. reschedule) their own pending
        # appointments; they cannot directly flip status to
        # approved/completed via this endpoint - that's what the
        # dedicated /status/ action below is for.
        if user.role == "patient":
            if instance.patient.user_id != user.id:
                return Response({"detail": "Not your appointment."}, status=403)

            data = {k: v for k, v in request.data.items() if k != "status"}
            partial = kwargs.get("partial", False)
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if user.role == "doctor" and instance.doctor.user_id != user.id:
            return Response({"detail": "Not your appointment."}, status=403)

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """
        PATCH /api/v1/appointments/{id}/status/
        Body: { "status": "approved" }

        - doctor/admin/receptionist: can set to approved/completed/cancelled.
        - patient: can only set to 'cancelled' (cancel their own appointment).
        """
        appointment = self.get_object()
        user = request.user
        new_status = request.data.get("status")

        if user.role == "patient":
            if appointment.patient.user_id != user.id:
                return Response({"detail": "Not your appointment."}, status=403)
            if new_status != Appointment.Status.CANCELLED:
                return Response(
                    {"detail": "Patients may only cancel their own appointments."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        elif user.role == "doctor":
            if appointment.doctor.user_id != user.id:
                return Response({"detail": "Not your appointment."}, status=403)

        serializer = AppointmentStatusUpdateSerializer(
            appointment, data={"status": new_status}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AppointmentSerializer(appointment).data)

    def destroy(self, request, *args, **kwargs):
        """
        Hard delete is restricted to admin/receptionist. Patients/doctors
        should use the cancel action (status=cancelled) instead of
        deleting the record outright, to preserve history.
        """
        if request.user.role not in ("admin", "receptionist"):
            return Response(
                {"detail": "Use the cancel action instead of deleting. "
                            "Only admin/receptionist can permanently delete appointments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
