from rest_framework import permissions


class IsMappingPatientOwner(permissions.BasePermission):
    """
    Object-level permission allowing operations only if the authenticated user
    owns the patient involved in the mapping.
    """

    def has_object_permission(self, request, view, obj):
        return obj.patient.created_by == request.user
