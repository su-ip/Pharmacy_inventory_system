import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

from apps.medicines.models import Medicine


class Batch(models.Model):
    """
    Represents a physical batch of a medicine.

    Example:

    Paracetamol 500mg
        ├── Batch PCM001 → 100 units
        ├── Batch PCM002 → 500 units
        └── Batch PCM003 → 250 units
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="batches"
    )

    batch_number = models.CharField(
        max_length=100
    )

    manufacturing_date = models.DateField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField()

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    mrp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["expiry_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["medicine", "batch_number"],
                name="unique_medicine_batch"
            )
        ]

        indexes = [
            models.Index(
                fields=["medicine", "expiry_date"]
            ),
            models.Index(
                fields=["expiry_date"]
            ),
            models.Index(
                fields=["batch_number"]
            ),
        ]

    def __str__(self):
        return f"{self.medicine} - {self.batch_number}"

class StockTransaction(models.Model):
    """
    Records every movement of stock.

    Quantity is ALWAYS positive.
    The transaction type determines whether stock increases
    or decreases.
    """

    class TransactionType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sale"
        SALES_RETURN = "SALES_RETURN", "Sales Return"
        PURCHASE_RETURN = "PURCHASE_RETURN", "Purchase Return"
        DAMAGE = "DAMAGE", "Damage"
        EXPIRED = "EXPIRED", "Expired"
        ADJUSTMENT_IN = "ADJUSTMENT_IN", "Adjustment In"
        ADJUSTMENT_OUT = "ADJUSTMENT_OUT", "Adjustment Out"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="stock_transactions"
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TransactionType.choices
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_transactions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["batch", "-created_at"]
            ),
            models.Index(
                fields=["transaction_type"]
            ),
            models.Index(
                fields=["created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.batch} | "
            f"{self.transaction_type} | "
            f"{self.quantity}"
        )