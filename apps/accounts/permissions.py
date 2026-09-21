from rest_framework.permissions import BasePermission

from apps.accounts.models import UserProfile


class HasRole(BasePermission):
    """
    Base permission for checking a user's UserProfile role.
    """

    allowed_roles = set()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Django superusers always have full access.
        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return False

        if not profile.is_active:
            return False

        return profile.role in self.allowed_roles


class IsAdmin(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
    }


class IsAdminOrPharmacist(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
    }


class CanManageInventory(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
        UserProfile.Role.STOREKEEPER,
    }


class CanSell(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
        UserProfile.Role.CASHIER,
    }


class CanManagePurchases(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
        UserProfile.Role.STOREKEEPER,
    }


class CanManageMedicines(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
    }


class CanManageCustomers(HasRole):
    allowed_roles = {
        UserProfile.Role.ADMIN,
        UserProfile.Role.PHARMACIST,
        UserProfile.Role.CASHIER,
    }