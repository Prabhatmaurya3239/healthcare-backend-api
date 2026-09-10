from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint to register a new user.
    Open to unauthenticated users. Returns 201 Created on success.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = {
            'message': 'User registered successfully.',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'date_joined': user.date_joined,
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint to obtain JWT access and refresh token pair using email and password.
    Open to unauthenticated users.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
