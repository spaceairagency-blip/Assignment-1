from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdminOrReceptionist
from .models import Doctor
from .serializers import (
    DoctorSerializer,
    DoctorCreateSerializer,
    DoctorAvailabilitySerializer,
)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Doctors.

    - list/retrieve: any authenticated user (patients need to browse
      doctors to book appointments).
    - create/update/delete: admin or receptionist only.
    - A doctor can update their OWN availability via the
      `set-availability` custom action, or via PATCH on their own record.

    Filters:
      ?department=<id>
      ?is_available=true|false
      ?specialization=Cardiology
      ?search=<name or specialization>
    """

    queryset = Doctor.objects.select_related("user", "department").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "is_available", "specialization"]
    search_fields = ["user__first_name", "user__last_name", "specialization", "user__username"]
    ordering_fields = ["experience", "id"]

    def get_serializer_class(self):
        if self.action == "create":
            return DoctorCreateSerializer
        return DoctorSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        # Allow a doctor to edit their own profile fields too (not just
        # admin/receptionist), e.g. updating phone or specialization.
        instance = self.get_object()
        user = request.user
        if user.role == "doctor" and instance.user_id == user.id:
            partial = kwargs.pop("partial", False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="set-availability")
    def set_availability(self, request, pk=None):
        """
        PATCH /api/v1/doctors/{id}/set-availability/
        Body: { "is_available": true }
        Allowed for: admin, receptionist, or the doctor themself.
        """
        doctor = self.get_object()
        user = request.user
        if not (
            user.role in ("admin", "receptionist")
            or (user.role == "doctor" and doctor.user_id == user.id)
        ):
            return Response(
                {"detail": "You do not have permission to update this doctor's availability."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DoctorAvailabilitySerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DoctorSerializer(doctor).data)

    @action(detail=False, methods=["get"], url_path="available")
    def available(self, request):
        """GET /api/v1/doctors/available/ -> only doctors currently available."""
        queryset = self.filter_queryset(self.get_queryset().filter(is_available=True))
        page = self.paginate_queryset(queryset)
        serializer = DoctorSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
