from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.accounts.models import UserProfile
from apps.accounts.permissions import (
    IsAdmin,
    CanManageInventory,
    CanSell,
    CanManagePurchases,
    CanManageMedicines,
    CanManageCustomers,
)


User = get_user_model()


class RolePermissionTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin = User.objects.create_user(
            username="test_admin",
            password="password123",
        )
        self.admin.profile.role = UserProfile.Role.ADMIN
        self.admin.profile.save()

        self.pharmacist = User.objects.create_user(
            username="test_pharmacist",
            password="password123",
        )
        self.pharmacist.profile.role = UserProfile.Role.PHARMACIST
        self.pharmacist.profile.save()

        self.cashier = User.objects.create_user(
            username="test_cashier",
            password="password123",
        )
        self.cashier.profile.role = UserProfile.Role.CASHIER
        self.cashier.profile.save()

        self.storekeeper = User.objects.create_user(
            username="test_storekeeper",
            password="password123",
        )
        self.storekeeper.profile.role = UserProfile.Role.STOREKEEPER
        self.storekeeper.profile.save()

    def make_request(self, user):
        request = self.factory.get("/test/")
        request.user = user
        return request

    def test_admin_has_admin_permission(self):
        request = self.make_request(self.admin)

        permission = IsAdmin()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_pharmacist_cannot_access_admin_only(self):
        request = self.make_request(self.pharmacist)

        permission = IsAdmin()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_cashier_can_sell(self):
        request = self.make_request(self.cashier)

        permission = CanSell()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_storekeeper_cannot_sell(self):
        request = self.make_request(self.storekeeper)

        permission = CanSell()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_storekeeper_can_manage_inventory(self):
        request = self.make_request(self.storekeeper)

        permission = CanManageInventory()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_cashier_cannot_manage_inventory(self):
        request = self.make_request(self.cashier)

        permission = CanManageInventory()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_pharmacist_can_manage_medicines(self):
        request = self.make_request(self.pharmacist)

        permission = CanManageMedicines()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_cashier_can_manage_customers(self):
        request = self.make_request(self.cashier)

        permission = CanManageCustomers()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_storekeeper_can_manage_purchases(self):
        request = self.make_request(self.storekeeper)

        permission = CanManagePurchases()

        self.assertTrue(
            permission.has_permission(request, None)
        )