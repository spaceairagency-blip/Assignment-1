from django.db import models


class Prescription(models.Model):
    """
    ERD: Prescription(id, appointment (OneToOneField -> Appointment),
    diagnosis (TextField), notes (TextField), created_at (DateTimeField))
    """

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="prescription",
    )
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prescription #{self.id} for Appointment #{self.appointment_id}"


class PrescriptionMedicine(models.Model):
    """
    ERD: PrescriptionMedicine(id, prescription (FK -> Prescription),
    medicine (FK -> Medicine), dosage, duration)

    This is the join table that lets a single Prescription contain
    multiple Medicines, each with its own dosage/duration.
    """

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="prescription_medicines",
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="prescription_medicines",
    )
    dosage = models.CharField(max_length=100, help_text="e.g. '500mg twice a day'")
    duration = models.CharField(max_length=100, help_text="e.g. '5 days'")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.medicine.name} - {self.dosage} ({self.duration})"
