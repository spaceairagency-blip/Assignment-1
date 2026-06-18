from django.db import models


class Department(models.Model):
    """ERD: Department(id, name, description)"""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
