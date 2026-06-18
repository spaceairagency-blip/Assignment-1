from rest_framework import serializers

from patients.serializers import PatientSerializer
from .models import Bill


class BillSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)

    class Meta:
        model = Bill
        fields = ("id", "patient", "patient_detail", "amount", "paid", "created_at")
        read_only_fields = ("created_at",)


class BillCreateSerializer(serializers.ModelSerializer):
    """Used to generate a bill for a patient."""

    class Meta:
        model = Bill
        fields = ("id", "patient", "amount", "paid")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def to_representation(self, instance):
        return BillSerializer(instance, context=self.context).data


class MarkPaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ("id", "paid")
