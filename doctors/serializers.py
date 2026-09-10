import re
from rest_framework import serializers
from doctors.models import Doctor

PHONE_REGEX = re.compile(r'^\+?[1-9]\d{6,14}$')


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor entities.
    Validates name, specialization, phone format, and professional email.
    """

    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'specialization',
            'phone',
            'email',
            'created_at',
            'updated_at',
            'created_by',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Doctor name cannot be empty.')
        return value.strip()

    def validate_specialization(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Specialization cannot be empty.')
        return value.strip()

    def validate_phone(self, value):
        cleaned_phone = value.strip().replace(' ', '').replace('-', '')
        if not PHONE_REGEX.match(cleaned_phone):
            raise serializers.ValidationError(
                'Invalid phone format. Please provide a valid phone number (e.g., +1234567890).'
            )
        return cleaned_phone

    def validate_email(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Doctor email cannot be empty.')
        return value.strip().lower()
