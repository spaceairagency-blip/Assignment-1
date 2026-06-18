from django.db import models


class Appointment(models.Model):
    """
    ERD: Appointment(id, patient (FK -> Patient), doctor (FK -> Doctor),
    appointment_date (DateTimeField), status (pending, approved, completed,
    cancelled), created_at (DateTimeField))
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    appointment_date = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appointment_date"]

    def __str__(self):
        return f"Appointment #{self.id} - {self.patient} with {self.doctor} on {self.appointment_date}"
