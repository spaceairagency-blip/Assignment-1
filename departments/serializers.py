from rest_framework import serializers

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    doctor_count = serializers.IntegerField(source="doctors.count", read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "description", "doctor_count")
