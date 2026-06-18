from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "age", "gender", "blood_group", "phone")
    list_filter = ("gender", "blood_group")
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone")
