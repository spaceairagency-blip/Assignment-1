from django.conf import settings
from django.db import models


class Patient(models.Model):
    """
    ERD: Patient(id, user (OneToOneField -> User), age (PositiveIntegerField),
    gender, blood_group, address (TextField), phone)
    """

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
