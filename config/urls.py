"""
Root URL configuration for the Hospital Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/departments/", include("departments.urls")),
    path("api/v1/doctors/", include("doctors.urls")),
    path("api/v1/patients/", include("patients.urls")),
    path("api/v1/appointments/", include("appointments.urls")),
    path("api/v1/medicines/", include("medicines.urls")),
    path("api/v1/prescriptions/", include("prescriptions.urls")),
    path("api/v1/billing/", include("billing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
