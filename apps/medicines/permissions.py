from rest_framework.permissions import BasePermission

from apps.accounts.models import UserProfile


class MedicinePermission(BasePermission):
    """
    Authenticated users can view medicines.

    Only Admin and Pharmacist can create/update medicines.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return False

        if not profile.is_active:
            return False

        return profile.role in {
            UserProfile.Role.ADMIN,
            UserProfile.Role.PHARMACIST,
        }