from rest_framework import permissions


class IsDoctorCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Any authenticated user can read doctor listings and details.
    - Only the user who registered the doctor can update or delete it.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.is_staff
