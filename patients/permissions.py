from rest_framework import permissions


class IsPatientOwner(permissions.BasePermission):
    """
    Object-level permission to ensure only the creator/owner of a patient
    can view, edit, or delete the record.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
