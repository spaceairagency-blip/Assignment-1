import django_filters

from .models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    """
    Supports:
      ?doctor=<id>
      ?patient=<id>
      ?status=pending|approved|completed|cancelled
      ?date=2026-06-20            (exact date)
      ?date_from=2026-06-01&date_to=2026-06-30   (date range)
    """

    date = django_filters.DateFilter(field_name="appointment_date", lookup_expr="date")
    date_from = django_filters.DateFilter(field_name="appointment_date", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="appointment_date", lookup_expr="date__lte")

    class Meta:
        model = Appointment
        fields = ["doctor", "patient", "status", "date", "date_from", "date_to"]
