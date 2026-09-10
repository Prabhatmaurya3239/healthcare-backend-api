from django.http import Http404
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mappings.models import PatientDoctorMapping
from mappings.serializers import (
    AssignedDoctorSerializer,
    PatientDoctorMappingSerializer,
)
from patients.models import Patient


class MappingListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating Patient-Doctor mappings.
    - GET /api/mappings/: Returns only mappings for patients owned by the authenticated user.
    - POST /api/mappings/: Creates a new mapping, validating patient ownership and preventing duplicates.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PatientDoctorMappingSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PatientDoctorMapping.objects.none()
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related('patient', 'doctor')


class PatientDoctorsListView(generics.ListAPIView):
    """
    Option A RESTful Endpoint:
    GET /api/mappings/patient/<patient_id>/
    Returns all doctors assigned to the specified patient.
    Strictly restricted to the patient's owner.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AssignedDoctorSerializer

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        try:
            patient = Patient.objects.get(pk=patient_id, created_by=self.request.user)
        except Patient.DoesNotExist:
            raise Http404('Patient not found or access denied.')

        return PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')


class MappingDetailOrPatientDoctorsView(views.APIView):
    """
    Dual-Compatibility Resolver for /api/mappings/<id>/:
    Resolves the URL ambiguity between:
      1. GET /api/mappings/<patient_id>/ (Assessment requirement for listing patient's doctors)
      2. DELETE /api/mappings/<mapping_id>/ (Assessment requirement for deleting mapping by ID)

    By inspecting the HTTP verb:
      - GET: Resolves <id> as patient_id, returning the assigned doctors if owned by request.user.
      - DELETE: Resolves <id> as mapping_id, deleting the mapping if owned by request.user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve all doctors assigned to patient with ID = pk.
        Enforces that request.user owns the patient.
        """
        try:
            patient = Patient.objects.get(pk=pk, created_by=request.user)
        except Patient.DoesNotExist:
            return Response(
                {'detail': 'Patient not found or access denied.'},
                status=status.HTTP_404_NOT_FOUND
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        serializer = AssignedDoctorSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete mapping with ID = pk.
        Enforces that request.user owns the patient associated with this mapping.
        """
        try:
            mapping = PatientDoctorMapping.objects.select_related('patient').get(
                pk=pk,
                patient__created_by=request.user
            )
        except PatientDoctorMapping.DoesNotExist:
            return Response(
                {'detail': 'Mapping not found or access denied.'},
                status=status.HTTP_404_NOT_FOUND
            )

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
