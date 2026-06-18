from django.db import transaction
from rest_framework import serializers

from medicines.models import Medicine
from .models import Prescription, PrescriptionMedicine


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = PrescriptionMedicine
        fields = ("id", "medicine", "medicine_name", "dosage", "duration")


class PrescriptionSerializer(serializers.ModelSerializer):
    """Read serializer, includes the nested list of prescribed medicines."""

    medicines = PrescriptionMedicineSerializer(
        source="prescription_medicines", many=True, read_only=True
    )
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = (
            "id",
            "appointment",
            "patient_name",
            "doctor_name",
            "diagnosis",
            "notes",
            "created_at",
            "medicines",
        )
        read_only_fields = ("created_at",)

    def get_patient_name(self, obj):
        user = obj.appointment.patient.user
        return user.get_full_name() or user.username

    def get_doctor_name(self, obj):
        user = obj.appointment.doctor.user
        return user.get_full_name() or user.username


class PrescriptionMedicineInputSerializer(serializers.Serializer):
    """Used only for input validation when creating a prescription with medicines."""

    medicine = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.all())
    dosage = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=100)


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """
    Create a prescription along with multiple medicines in one request.

    Example payload:
    {
      "appointment": 5,
      "diagnosis": "Acute bronchitis",
      "notes": "Follow up in 1 week",
      "medicines": [
        {"medicine": 1, "dosage": "500mg twice a day", "duration": "5 days"},
        {"medicine": 3, "dosage": "1 tablet at night", "duration": "7 days"}
      ]
    }
    """

    medicines = PrescriptionMedicineInputSerializer(many=True, write_only=True)

    class Meta:
        model = Prescription
        fields = ("id", "appointment", "diagnosis", "notes", "medicines")

    def validate_appointment(self, appointment):
        if hasattr(appointment, "prescription"):
            raise serializers.ValidationError(
                "This appointment already has a prescription."
            )
        return appointment

    def validate_medicines(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one medicine must be included in the prescription."
            )
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        appointment = attrs.get("appointment")

        # A doctor may only write prescriptions for their own appointments.
        if user.role == "doctor" and appointment.doctor.user_id != user.id:
            raise serializers.ValidationError(
                "You can only create prescriptions for your own appointments."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        medicines_data = validated_data.pop("medicines")
        prescription = Prescription.objects.create(**validated_data)

        PrescriptionMedicine.objects.bulk_create(
            [
                PrescriptionMedicine(
                    prescription=prescription,
                    medicine=item["medicine"],
                    dosage=item["dosage"],
                    duration=item["duration"],
                )
                for item in medicines_data
            ]
        )
        return prescription

    def to_representation(self, instance):
        return PrescriptionSerializer(instance, context=self.context).data
