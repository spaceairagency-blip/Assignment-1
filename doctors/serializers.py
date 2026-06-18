from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Doctor

User = get_user_model()


class DoctorSerializer(serializers.ModelSerializer):
    """
    Used for read operations (list/retrieve) and for updates on an
    existing doctor's own profile fields. Nests full user details.
    """

    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user",
            "department",
            "department_name",
            "specialization",
            "phone",
            "experience",
            "is_available",
        )


class DoctorCreateSerializer(serializers.ModelSerializer):
    """
    Used for creating a Doctor. Supports two flows:

    1. Admin/receptionist creates a brand new doctor: pass nested
       `username`, `email`, `password` to create the underlying User
       at the same time as the Doctor profile.
    2. Attaching a Doctor profile to an already-registered user account
       (one created via /auth/register/ with role=doctor): pass
       `user_id` instead.
    """

    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.DOCTOR),
        write_only=True,
        required=False,
        source="user",
    )

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user_id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "department",
            "specialization",
            "phone",
            "experience",
            "is_available",
        )

    def validate(self, attrs):
        has_user_id = "user" in attrs
        has_new_user_fields = all(
            k in attrs for k in ("username", "email", "password")
        )
        if not has_user_id and not has_new_user_fields:
            raise serializers.ValidationError(
                "Provide either 'user_id' (existing user with role=doctor) "
                "or 'username', 'email', and 'password' to create a new doctor account."
            )
        if has_user_id and hasattr(attrs["user"], "doctor_profile"):
            raise serializers.ValidationError(
                "This user already has a doctor profile."
            )
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
                role=User.Role.DOCTOR,
            )
        else:
            validated_data.pop("username", None)
            validated_data.pop("email", None)
            validated_data.pop("password", None)
            validated_data.pop("first_name", None)
            validated_data.pop("last_name", None)

        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

    def to_representation(self, instance):
        return DoctorSerializer(instance, context=self.context).data


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    """Minimal serializer for toggling a doctor's availability."""

    class Meta:
        model = Doctor
        fields = ("id", "is_available")
