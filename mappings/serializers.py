from rest_framework import serializers
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing Patient-Doctor mappings.
    Enforces that the authenticated user must own the patient,
    and prevents duplicate assignments.
    """

    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient',
            'doctor',
            'patient_name',
            'doctor_name',
            'doctor_specialization',
            'assigned_at',
        )
        read_only_fields = ('id', 'assigned_at', 'patient_name', 'doctor_name', 'doctor_specialization')

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Ownership authorization check: user must own the patient
        if request and request.user:
            if patient.created_by != request.user:
                raise serializers.ValidationError({
                    'patient': 'You are only authorized to assign doctors to patients that you own.'
                })

        # Duplicate check before database insert
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['This doctor is already assigned to the specified patient.']
            })

        return attrs


class AssignedDoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for representing doctors assigned to a specific patient,
    including the mapping ID and assignment timestamp.
    """

    mapping_id = serializers.IntegerField(source='id', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    phone = serializers.CharField(source='doctor.phone', read_only=True)
    email = serializers.EmailField(source='doctor.email', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'mapping_id',
            'doctor_id',
            'doctor_name',
            'specialization',
            'phone',
            'email',
            'assigned_at',
        )
