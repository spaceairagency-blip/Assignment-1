from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from config.permissions import ReadOnlyOrAdminReceptionist
from .models import Medicine
from .serializers import MedicineSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    """
    List / Search medicines, plus full CRUD for admin/receptionist
    (someone needs to be able to add medicines to the catalog).

    GET /api/v1/medicines/?search=paracetamol
    """

    queryset = Medicine.objects.all().order_by("name")
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrAdminReceptionist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "unit"]
    ordering_fields = ["name", "id"]
