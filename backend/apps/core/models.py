"""
Shared abstract models for the Showcase project.

All concrete models should inherit from TimeStampedModel to ensure
consistent created_at / updated_at tracking across the application.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model providing self-managed timestamp fields.

    Attributes:
        created_at: Automatically set when the record is first created.
        updated_at: Automatically updated every time the record is saved.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
