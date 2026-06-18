from django.db import models


class Bill(models.Model):
    """
    ERD: Bill(id, patient (FK -> Patient), amount (DecimalField),
    paid (BooleanField), created_at (DateTimeField))
    """

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="bills",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"Bill #{self.id} - {self.patient} - {self.amount} ({status})"
