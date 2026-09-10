from django.db import models


class PatientDoctorMapping(models.Model):
    """
    Associative mapping entity representing the assignment of a Doctor to a Patient.
    Enforces referential integrity and unique assignment via database-level constraint.
    """

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text='The patient being assigned to a doctor.'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text='The doctor assigned to care for the patient.'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the assignment was established.'
    )

    class Meta:
        verbose_name = 'Patient-Doctor Mapping'
        verbose_name_plural = 'Patient-Doctor Mappings'
        ordering = ['-assigned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'doctor'],
                name='unique_patient_doctor'
            )
        ]
        indexes = [
            models.Index(fields=['patient', 'doctor']),
            models.Index(fields=['assigned_at']),
        ]

    def __str__(self):
        return f"Patient: {self.patient.name} <-> Doctor: {self.doctor.name}"
