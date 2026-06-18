from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "specialization", "experience", "is_available")
    list_filter = ("department", "is_available", "specialization")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialization")
