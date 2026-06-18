"""
Reusable role-based permission classes for the Hospital Management System.

These are imported by every app's views.py so that role checks stay
consistent across the whole project.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsDoctor(BasePermission):
    """Allows access only to doctor users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "doctor"
        )


class IsPatient(BasePermission):
    """Allows access only to patient users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "patient"
        )


class IsReceptionist(BasePermission):
    """Allows access only to receptionist users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "receptionist"
        )


class IsAdminOrReceptionist(BasePermission):
    """Allows access to admin or receptionist users (front-desk staff)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "receptionist")
        )


class IsAdminOrDoctor(BasePermission):
    """Allows access to admin or doctor users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "doctor")
        )


class IsOwnerOrStaff(BasePermission):
    """
    Object-level permission: allows access if the requesting user owns
    the object (object has a `user` attribute matching request.user, or
    the object itself is the request.user), or if the requester is staff
    (admin/receptionist/doctor depending on view-level permission_classes).

    Falls back to staff roles (admin, receptionist) always being allowed
    full access at the object level.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in ("admin", "receptionist"):
            return True

        owner = getattr(obj, "user", None)
        if owner is not None:
            return owner == user

        return obj == user


class ReadOnlyOrAdminReceptionist(BasePermission):
    """
    Anyone authenticated may perform safe (read-only) requests.
    Only admin/receptionist may perform write requests.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ("admin", "receptionist")
