from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from config.permissions import ReadOnlyOrAdminReceptionist
from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for departments.

    - Any authenticated user can list/retrieve departments.
    - Only admin/receptionist can create/update/delete departments.
    """

    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrAdminReceptionist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "id"]
