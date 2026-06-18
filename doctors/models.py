from django.conf import settings
from django.db import models


class Doctor(models.Model):
    """
    ERD: Doctor(id, user (OneToOneField -> User), department (FK -> Department),
    specialization, phone, experience (PositiveIntegerField), is_available (Boolean))
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctors",
    )
    specialization = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    experience = models.PositiveIntegerField(default=0, help_text="Years of experience")
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"
