from django.utils import timezone
from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient
from patients.serializers import PatientSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Read serializer with nested doctor/patient detail."""

    patient_detail = PatientSerializer(source="patient", read_only=True)
    doctor_detail = DoctorSerializer(source="doctor", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "patient_detail",
            "doctor",
            "doctor_detail",
            "appointment_date",
            "status",
            "created_at",
        )
        read_only_fields = ("created_at",)


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Used to book an appointment.

    - A patient booking for themself does not need to pass `patient`;
      it's inferred from request.user. Admin/receptionist must pass
      `patient` explicitly (they're booking on behalf of someone).
    """

    class Meta:
        model = Appointment
        fields = ("id", "patient", "doctor", "appointment_date", "status")
        read_only_fields = ("id",)

    def validate_doctor(self, doctor):
        if not doctor.is_available:
            raise serializers.ValidationError(
                "This doctor is currently not available for appointments."
            )
        return doctor

    def validate_appointment_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        if "patient" not in attrs:
            if user.role == "patient":
                try:
                    attrs["patient"] = user.patient_profile
                except Patient.DoesNotExist:
                    raise serializers.ValidationError(
                        "Your account does not have an associated patient profile yet."
                    )
            else:
                raise serializers.ValidationError(
                    {"patient": "This field is required when booking on behalf of a patient."}
                )

        doctor = attrs.get("doctor")
        appointment_date = attrs.get("appointment_date")
        patient = attrs.get("patient")

        # Prevent an obvious double-booking: same doctor, same exact slot,
        # not already cancelled.
        if doctor and appointment_date:
            clashing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
            ).exclude(status=Appointment.Status.CANCELLED)
            if self.instance:
                clashing = clashing.exclude(pk=self.instance.pk)
            if clashing.exists():
                raise serializers.ValidationError(
                    "This doctor already has an appointment booked at that exact time."
                )

        return attrs

    def to_representation(self, instance):
        return AppointmentSerializer(instance, context=self.context).data


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    """Used to update only the status of an appointment (approve/cancel/complete)."""

    class Meta:
        model = Appointment
        fields = ("id", "status")
