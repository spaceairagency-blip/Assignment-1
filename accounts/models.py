from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model as per the ERD.

    AbstractUser already provides: id (BigAutoField), username, email,
    password, first_name, last_name, date_joined (it's called
    `date_joined` natively in Django's AbstractUser) plus the usual
    is_active/is_staff/is_superuser flags that Django's auth system
    relies on. We only need to add the `role` field on top.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"
        RECEPTIONIST = "receptionist", "Receptionist"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST
