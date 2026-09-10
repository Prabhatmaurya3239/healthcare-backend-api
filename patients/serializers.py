import re
from rest_framework import serializers
from patients.models import Patient

# E.164 compatible or standard phone regex: optional '+' followed by 7 to 15 digits
PHONE_REGEX = re.compile(r'^\+?[1-9]\d{6,14}$')


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient entities.
    Enforces healthcare-compatible validation rules for age, phone, and name.
    Ownership is strictly managed by the server and cannot be altered by clients.
    """

    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
            'age',
            'gender',
            'phone',
            'address',
            'medical_history',
            'created_at',
            'updated_at',
            'created_by',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Patient name cannot be empty.')
        return value.strip()

    def validate_age(self, value):
        """
        Validates that age falls within a medically plausible human lifespan (0 to 120 years).
        Rejects negative numbers and values exceeding 120.
        """
        if value < 0:
            raise serializers.ValidationError('Age must be a positive integer.')
        if value > 120:
            raise serializers.ValidationError('Age must be within a realistic lifespan (0-120 years).')
        return value

    def validate_phone(self, value):
        """
        Validates phone number against standard E.164 telecommunication formatting.
        Allows an optional leading '+' followed by 7 to 15 digits.
        """
        cleaned_phone = value.strip().replace(' ', '').replace('-', '')
        if not PHONE_REGEX.match(cleaned_phone):
            raise serializers.ValidationError(
                'Invalid phone format. Please provide a valid phone number (e.g., +1234567890 or 9876543210).'
            )
        return cleaned_phone

    def validate_address(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Address cannot be empty.')
        return value.strip()
