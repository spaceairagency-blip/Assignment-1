from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdminOrReceptionist
from .models import Patient
from .serializers import PatientSerializer, PatientCreateSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Patients.

    - admin/receptionist: full access to all patients.
    - doctor: read-only access to all patients (needed to view who
      they're treating).
    - patient: can view and update only their OWN record.
    """

    queryset = Patient.objects.select_related("user").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["gender", "blood_group"]
    search_fields = ["user__first_name", "user__last_name", "user__username", "phone"]
    ordering_fields = ["age", "id"]

    def get_serializer_class(self):
        if self.action == "create":
            return PatientCreateSerializer
        return PatientSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsAdminOrReceptionist()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "patient":
            return qs.filter(user=user)
        # admin, receptionist, doctor can see all patients
        return qs

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.role == "patient" and instance.user_id != user.id:
            return Response(
                {"detail": "You can only update your own patient record."},
                status=403,
            )
        if user.role == "doctor":
            return Response(
                {"detail": "Doctors have read-only access to patient records."},
                status=403,
            )
        return super().update(request, *args, **kwargs)
