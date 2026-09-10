from django.conf import settings
from django.db import models


class Patient(models.Model):
    """
    Patient entity representing an individual's demographic and medical record.
    Strictly owned and managed by the user who created it.
    """

    GENDER_MALE = 'Male'
    GENDER_FEMALE = 'Female'
    GENDER_OTHER = 'Other'

    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    name = models.CharField(
        max_length=255,
        help_text='Full legal name of the patient.'
    )
    age = models.PositiveIntegerField(
        help_text='Age of the patient in years (0-120).'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text='Gender identity of the patient.'
    )
    phone = models.CharField(
        max_length=20,
        help_text='Primary contact telephone number.'
    )
    address = models.TextField(
        help_text='Residential address.'
    )
    medical_history = models.TextField(
        blank=True,
        default='',
        help_text='Past medical conditions, allergies, or clinical notes.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the patient record was registered.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the patient record was last updated.'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        help_text='Authenticated user who registered and owns this patient record.'
    )

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} (ID: {self.id})"
