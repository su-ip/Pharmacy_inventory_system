import uuid

from django.db import models
from django.core.validators import MinValueValidator


class TimeStampedModel(models.Model):
    """
    Base model providing UUID, created_at and updated_at.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """
    Medicine category.

    Examples:
    - Antibiotics
    - Painkillers
    - Vitamins
    - Antacids
    """

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Manufacturer(TimeStampedModel):
    """
    Company that manufactures the medicine.
    """

    name = models.CharField(
        max_length=200,
        unique=True
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Medicine(TimeStampedModel):
    """
    Master record for a medicine.

    Stock is NOT stored here.
    Stock belongs to individual batches.
    """

    class DosageForm(models.TextChoices):
        TABLET = "TABLET", "Tablet"
        CAPSULE = "CAPSULE", "Capsule"
        SYRUP = "SYRUP", "Syrup"
        INJECTION = "INJECTION", "Injection"
        CREAM = "CREAM", "Cream"
        OINTMENT = "OINTMENT", "Ointment"
        DROPS = "DROPS", "Drops"
        INHALER = "INHALER", "Inhaler"
        OTHER = "OTHER", "Other"

    name = models.CharField(
        max_length=200
    )

    generic_name = models.CharField(
        max_length=200,
        blank=True
    )

    brand_name = models.CharField(
        max_length=200,
        blank=True
    )

    strength = models.CharField(
        max_length=100,
        blank=True
    )

    dosage_form = models.CharField(
        max_length=20,
        choices=DosageForm.choices,
        default=DosageForm.TABLET
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="medicines"
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name="medicines"
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    reorder_level = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "strength",
                    "dosage_form",
                    "manufacturer",
                ],
                name="unique_medicine_combination"
            )
        ]

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["generic_name"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self):
        if self.strength:
            return f"{self.name} {self.strength}"

        return self.name