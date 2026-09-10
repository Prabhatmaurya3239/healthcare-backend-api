from django.conf import settings
from django.db import models


class Doctor(models.Model):
    """
    Doctor entity representing a medical practitioner who can be assigned to patients.
    """

    name = models.CharField(
        max_length=255,
        help_text='Full professional name of the doctor.'
    )
    specialization = models.CharField(
        max_length=255,
        help_text='Medical discipline or clinical specialization (e.g., Cardiology, Neurology).'
    )
    phone = models.CharField(
        max_length=20,
        help_text='Contact phone number.'
    )
    email = models.EmailField(
        max_length=255,
        help_text='Professional email address.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the doctor record was created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the doctor record was last updated.'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctors',
        help_text='User who registered this doctor.'
    )

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['specialization']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"
