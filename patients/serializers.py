from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Patient

User = get_user_model()


class PatientSerializer(serializers.ModelSerializer):
    """Used for read operations and updates on an existing patient."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "age",
            "gender",
            "blood_group",
            "address",
            "phone",
        )


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Creates a Patient profile. Supports either:
    1. user_id of an already-registered user with role=patient, or
    2. inline username/email/password to create the user on the fly.
    """

    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.PATIENT),
        write_only=True,
        required=False,
        source="user",
    )

    class Meta:
        model = Patient
        fields = (
            "id",
            "user_id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "age",
            "gender",
            "blood_group",
            "address",
            "phone",
        )

    def validate(self, attrs):
        has_user_id = "user" in attrs
        has_new_user_fields = all(
            k in attrs for k in ("username", "email", "password")
        )
        if not has_user_id and not has_new_user_fields:
            raise serializers.ValidationError(
                "Provide either 'user_id' (existing user with role=patient) "
                "or 'username', 'email', and 'password' to create a new patient account."
            )
        if has_user_id and hasattr(attrs["user"], "patient_profile"):
            raise serializers.ValidationError("This user already has a patient profile.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data.pop("user", None)

        if user is None:
            username = validated_data.pop("username")
            email = validated_data.pop("email")
            password = validated_data.pop("password")
            first_name = validated_data.pop("first_name", "")
            last_name = validated_data.pop("last_name", "")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.PATIENT,
            )
        else:
            validated_data.pop("username", None)
            validated_data.pop("email", None)
            validated_data.pop("password", None)
            validated_data.pop("first_name", None)
            validated_data.pop("last_name", None)

        patient = Patient.objects.create(user=user, **validated_data)
        return patient

    def to_representation(self, instance):
        return PatientSerializer(instance, context=self.context).data
