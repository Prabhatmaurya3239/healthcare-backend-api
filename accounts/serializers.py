from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration.
    Validates email format, email uniqueness, non-empty name,
    and enforces Django standard password complexity rules.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='User password satisfying complexity constraints.'
    )

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Name cannot be empty or only whitespace.')
        return value.strip()

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError('A user with this email address already exists.')
        return normalized_email

    def validate_password(self, value):
        # Validate against Django configured password validators
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom SimpleJWT serializer that authenticates using email and password,
    returning both JWT tokens and user metadata.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
        }
        return data
