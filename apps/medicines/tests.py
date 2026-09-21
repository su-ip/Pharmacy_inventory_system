from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.medicines.models import Category, Manufacturer, Medicine


User = get_user_model()


class MedicineAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Antibiotics",
            description="Antibiotic medicines",
        )

        self.manufacturer = Manufacturer.objects.create(
            name="Test Pharma",
            phone="9800000000",
            email="test@pharma.com",
        )

        self.medicine = Medicine.objects.create(
            name="Amoxicillin",
            generic_name="Amoxicillin",
            brand_name="Amoxil",
            strength="500mg",
            dosage_form=Medicine.DosageForm.CAPSULE,
            category=self.category,
            manufacturer=self.manufacturer,
            barcode="1234567890",
            reorder_level=10,
        )

        self.admin = User.objects.create_user(
            username="medicine_admin",
            password="password123",
        )
        self.admin.profile.role = UserProfile.Role.ADMIN
        self.admin.profile.save()

        self.pharmacist = User.objects.create_user(
            username="medicine_pharmacist",
            password="password123",
        )
        self.pharmacist.profile.role = UserProfile.Role.PHARMACIST
        self.pharmacist.profile.save()

        self.cashier = User.objects.create_user(
            username="medicine_cashier",
            password="password123",
        )
        self.cashier.profile.role = UserProfile.Role.CASHIER
        self.cashier.profile.save()

        self.storekeeper = User.objects.create_user(
            username="medicine_storekeeper",
            password="password123",
        )
        self.storekeeper.profile.role = UserProfile.Role.STOREKEEPER
        self.storekeeper.profile.save()

    def medicine_data(self):
        return {
            "name": "Paracetamol",
            "generic_name": "Paracetamol",
            "brand_name": "Crocin",
            "strength": "500mg",
            "dosage_form": Medicine.DosageForm.TABLET,
            "category": str(self.category.id),
            "manufacturer": str(self.manufacturer.id),
            "barcode": "9876543210",
            "reorder_level": 20,
            "is_active": True,
        }

    def test_authenticated_user_can_view_medicines(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get("/api/medicines/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_unauthenticated_user_cannot_view_medicines(self):
        response = self.client.get("/api/medicines/")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_medicine(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/medicines/",
            self.medicine_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Medicine.objects.filter(
                name="Paracetamol"
            ).count(),
            1,
        )

    def test_pharmacist_can_create_medicine(self):
        self.client.force_authenticate(user=self.pharmacist)

        response = self.client.post(
            "/api/medicines/",
            self.medicine_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_cashier_cannot_create_medicine(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.post(
            "/api/medicines/",
            self.medicine_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_storekeeper_cannot_create_medicine(self):
        self.client.force_authenticate(user=self.storekeeper)

        response = self.client.post(
            "/api/medicines/",
            self.medicine_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_cashier_can_search_medicines(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/medicines/?search=Amoxicillin"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_search_nonexistent_medicine(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/medicines/?search=Ibuprofen"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_dosage_form(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/medicines/?dosage_form=CAPSULE"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_filter_active_medicines(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/medicines/?is_active=true"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_admin_can_update_medicine(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/medicines/{self.medicine.id}/",
            {
                "strength": "650mg",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.medicine.refresh_from_db()

        self.assertEqual(
            self.medicine.strength,
            "650mg",
        )

    def test_cashier_cannot_update_medicine(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.patch(
            f"/api/medicines/{self.medicine.id}/",
            {
                "strength": "650mg",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_medicine_can_be_deactivated(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f"/api/medicines/{self.medicine.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.medicine.refresh_from_db()

        self.assertFalse(self.medicine.is_active)

    def test_category_api(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/categories/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_manufacturer_api(self):
        self.client.force_authenticate(user=self.cashier)

        response = self.client.get(
            "/api/manufacturers/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)