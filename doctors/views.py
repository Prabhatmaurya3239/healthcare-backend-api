from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from doctors.models import Doctor
from doctors.permissions import IsDoctorCreatorOrReadOnly
from doctors.serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Doctor profiles.
    Allows authenticated users to browse doctors, and creators to update/delete them.
    """

    queryset = Doctor.objects.all().select_related('created_by')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorCreatorOrReadOnly]

    def perform_create(self, serializer):
        """
        Record the authenticated user as the creator.
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Preserve original creator during updates.
        """
        serializer.save(created_by=self.get_object().created_by)
