from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from patients.models import Patient
from patients.permissions import IsPatientOwner
from patients.serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Patient records.
    Requires authentication for all actions.
    Enforces strict data isolation: users can only view, update, or delete
    patient records that they themselves created.
    """

    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOwner]

    def get_queryset(self):
        """
        Scope queryset strictly to the authenticated user's patients.
        Prevents IDOR by returning 404 for any resource belonging to another tenant/user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user).select_related('created_by')

    def perform_create(self, serializer):
        """
        Automatically bind the authenticated user as the creator/owner.
        Client input for created_by is ignored.
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure ownership remains immutable during updates.
        """
        serializer.save(created_by=self.request.user)
