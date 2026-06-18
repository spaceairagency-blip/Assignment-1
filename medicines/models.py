from django.db import models


class Medicine(models.Model):
    """ERD: Medicine(id, name, description (TextField), unit)"""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, help_text="e.g. mg, ml, tablet, capsule")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.unit})"
