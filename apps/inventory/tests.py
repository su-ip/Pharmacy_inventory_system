from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.inventory.models import Batch, StockTransaction
from apps.medicines.models import Category, Manufacturer, Medicine


User = get_user_model()


class InventoryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Painkillers",
        )

        self.manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer",
        )

        self.medicine = Medicine.objects.create(
            name="Paracetamol",
            generic_name="Paracetamol",
            strength="500mg",
            dosage_form=Medicine.DosageForm.TABLET,
            category=self.category,
            manufacturer=self.manufacturer,
            reorder_level=10,
        )

        self.batch = Batch.objects.create(
            medicine=self.medicine,
            batch_number="PCM-001",
            manufacturing_date=date.today()
            - timedelta(days=30),
            expiry_date=date.today()
            + timedelta(days=365),
            purchase_price=10,
            selling_price=15,
            mrp=20,
            quantity=100,
            is_active=True,
        )

        self.admin = User.objects.create_user(
            username="inventory_admin",
            password="password123",
        )
        self.admin.profile.role = UserProfile.Role.ADMIN
        self.admin.profile.save()

        self.pharmacist = User.objects.create_user(
            username="inventory_pharmacist",
            password="password123",
        )
        self.pharmacist.profile.role = (
            UserProfile.Role.PHARMACIST
        )
        self.pharmacist.profile.save()

        self.storekeeper = User.objects.create_user(
            username="inventory_storekeeper",
            password="password123",
        )
        self.storekeeper.profile.role = (
            UserProfile.Role.STOREKEEPER
        )
        self.storekeeper.profile.save()

        self.cashier = User.objects.create_user(
            username="inventory_cashier",
            password="password123",
        )
        self.cashier.profile.role = (
            UserProfile.Role.CASHIER
        )
        self.cashier.profile.save()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # --------------------------------------------------
    # BATCH API
    # --------------------------------------------------

    def test_authenticated_user_can_view_batches(self):
        self.authenticate(self.cashier)

        response = self.client.get(
            "/api/inventory/batches/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_unauthenticated_user_cannot_view_batches(self):
        response = self.client.get(
            "/api/inventory/batches/"
        )

        self.assertEqual(response.status_code, 403)

    def test_batch_quantity_is_read_only(self):
        self.authenticate(self.storekeeper)

        response = self.client.patch(
            f"/api/inventory/batches/{self.batch.id}/",
            {
                "quantity": 9999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.batch.refresh_from_db()

        self.assertEqual(
            self.batch.quantity,
            100,
        )

    def test_storekeeper_can_create_batch(self):
        self.authenticate(self.storekeeper)

        data = {
            "medicine": str(self.medicine.id),
            "batch_number": "PCM-002",
            "manufacturing_date": str(
                date.today()
            ),
            "expiry_date": str(
                date.today() + timedelta(days=365)
            ),
            "purchase_price": "12.00",
            "selling_price": "18.00",
            "mrp": "20.00",
        }

        response = self.client.post(
            "/api/inventory/batches/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Batch.objects.filter(
                batch_number="PCM-002"
            ).exists()
        )

    def test_cashier_cannot_create_batch(self):
        self.authenticate(self.cashier)

        data = {
            "medicine": str(self.medicine.id),
            "batch_number": "PCM-003",
            "expiry_date": str(
                date.today() + timedelta(days=365)
            ),
            "purchase_price": "10.00",
            "selling_price": "15.00",
            "mrp": "20.00",
        }

        response = self.client.post(
            "/api/inventory/batches/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_create_expired_batch(self):
        self.authenticate(self.storekeeper)

        data = {
            "medicine": str(self.medicine.id),
            "batch_number": "EXPIRED-001",
            "expiry_date": str(
                date.today() - timedelta(days=1)
            ),
            "purchase_price": "10.00",
            "selling_price": "15.00",
            "mrp": "20.00",
        }

        response = self.client.post(
            "/api/inventory/batches/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_selling_price_cannot_exceed_mrp(self):
        self.authenticate(self.storekeeper)

        data = {
            "medicine": str(self.medicine.id),
            "batch_number": "PRICE-001",
            "expiry_date": str(
                date.today() + timedelta(days=365)
            ),
            "purchase_price": "10.00",
            "selling_price": "25.00",
            "mrp": "20.00",
        }

        response = self.client.post(
            "/api/inventory/batches/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_can_search_batches(self):
        self.authenticate(self.cashier)

        response = self.client.get(
            "/api/inventory/batches/?search=PCM-001"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    # --------------------------------------------------
    # STOCK ADJUSTMENT API
    # --------------------------------------------------

    def test_storekeeper_can_adjust_stock_out(self):
        self.authenticate(self.storekeeper)

        response = self.client.post(
            "/api/inventory/stock/adjust/",
            {
                "batch": str(self.batch.id),
                "quantity": 10,
                "transaction_type": "DAMAGE",
                "notes": "Damaged tablets",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.batch.refresh_from_db()

        self.assertEqual(
            self.batch.quantity,
            90,
        )

        self.assertTrue(
            StockTransaction.objects.filter(
                batch=self.batch,
                transaction_type="DAMAGE",
                quantity=10,
            ).exists()
        )

    def test_storekeeper_can_adjust_stock_in(self):
        self.authenticate(self.storekeeper)

        response = self.client.post(
            "/api/inventory/stock/adjust/",
            {
                "batch": str(self.batch.id),
                "quantity": 25,
                "transaction_type": "ADJUSTMENT_IN",
                "notes": "Stock count correction",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.batch.refresh_from_db()

        self.assertEqual(
            self.batch.quantity,
            125,
        )

    def test_cannot_remove_more_stock_than_available(self):
        self.authenticate(self.storekeeper)

        response = self.client.post(
            "/api/inventory/stock/adjust/",
            {
                "batch": str(self.batch.id),
                "quantity": 1000,
                "transaction_type": "DAMAGE",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.batch.refresh_from_db()

        self.assertEqual(
            self.batch.quantity,
            100,
        )

        self.assertFalse(
            StockTransaction.objects.filter(
                batch=self.batch,
                transaction_type="DAMAGE",
                quantity=1000,
            ).exists()
        )

    def test_cashier_cannot_adjust_stock(self):
        self.authenticate(self.cashier)

        response = self.client.post(
            "/api/inventory/stock/adjust/",
            {
                "batch": str(self.batch.id),
                "quantity": 10,
                "transaction_type": "DAMAGE",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------
    # TRANSACTION API
    # --------------------------------------------------

    def test_storekeeper_can_view_transactions(self):
        StockTransaction.objects.create(
            batch=self.batch,
            transaction_type=(
                StockTransaction.TransactionType.DAMAGE
            ),
            quantity=5,
            notes="Test damage",
            created_by=self.storekeeper,
        )

        self.authenticate(self.storekeeper)

        response = self.client.get(
            "/api/inventory/stock-transactions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_cashier_cannot_view_transactions(self):
        self.authenticate(self.cashier)

        response = self.client.get(
            "/api/inventory/stock-transactions/"
        )

        self.assertEqual(response.status_code, 403)

    def test_transactions_are_read_only(self):
        transaction = StockTransaction.objects.create(
            batch=self.batch,
            transaction_type=(
                StockTransaction.TransactionType.DAMAGE
            ),
            quantity=5,
            notes="Test damage",
            created_by=self.storekeeper,
        )

        self.authenticate(self.storekeeper)

        response = self.client.delete(
            f"/api/inventory/stock-transactions/"
            f"{transaction.id}/"
        )

        self.assertEqual(
            response.status_code,
            405,
        )