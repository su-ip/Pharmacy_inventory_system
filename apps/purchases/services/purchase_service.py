from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.models import Batch, StockTransaction
from apps.purchases.models import Purchase, PurchaseItem


@transaction.atomic
def create_purchase(
    *,
    supplier,
    invoice_number,
    purchase_date,
    items,
    created_by,
    discount=Decimal("0.00"),
    tax=Decimal("0.00"),
):
    """
    Create a completed purchase and update inventory.

    Everything happens inside one database transaction.

    If any operation fails, the entire purchase is rolled back.
    """

    if not items:
        raise ValueError("Purchase must contain at least one item.")

    # ---------------------------------------------------------
    # 1. Create the purchase
    # ---------------------------------------------------------

    purchase = Purchase.objects.create(
        supplier=supplier,
        invoice_number=invoice_number,
        purchase_date=purchase_date,
        discount=discount,
        tax=tax,
        created_by=created_by,
        status=Purchase.Status.DRAFT,
    )

    subtotal = Decimal("0.00")

    # ---------------------------------------------------------
    # 2. Process every purchase item
    # ---------------------------------------------------------

    for item in items:

        medicine = item["medicine"]

        batch_number = item["batch_number"]

        manufacturing_date = item.get(
            "manufacturing_date"
        )

        expiry_date = item["expiry_date"]

        quantity = int(item["quantity"])

        purchase_price = Decimal(
            str(item["purchase_price"])
        )

        selling_price = Decimal(
            str(item["selling_price"])
        )

        mrp = item.get("mrp")

        if mrp is not None:
            mrp = Decimal(str(mrp))

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        if quantity <= 0:
            raise ValueError(
                "Purchase quantity must be greater than zero."
            )

        if expiry_date < timezone.now().date():
            raise ValueError(
                f"Batch {batch_number} has already expired."
            )

        if purchase_price < 0:
            raise ValueError(
                "Purchase price cannot be negative."
            )

        if selling_price < 0:
            raise ValueError(
                "Selling price cannot be negative."
            )

        # -----------------------------------------------------
        # 3. Find or create the batch
        # -----------------------------------------------------

        batch, created = Batch.objects.get_or_create(
            medicine=medicine,
            batch_number=batch_number,
            defaults={
                "manufacturing_date": manufacturing_date,
                "expiry_date": expiry_date,
                "purchase_price": purchase_price,
                "selling_price": selling_price,
                "mrp": mrp,
                "quantity": 0,
                "is_active": True,
            },
        )

        # -----------------------------------------------------
        # 4. Lock the batch row
        # -----------------------------------------------------

        batch = Batch.objects.select_for_update().get(
            pk=batch.pk
        )

        # -----------------------------------------------------
        # 5. Update batch information
        # -----------------------------------------------------

        if not created:

            # Do not allow a previously expired batch
            # to receive new stock.
            if batch.expiry_date < timezone.now().date():
                raise ValueError(
                    f"Batch {batch.batch_number} is expired."
                )

            batch.manufacturing_date = (
                manufacturing_date
                if manufacturing_date is not None
                else batch.manufacturing_date
            )

            batch.expiry_date = expiry_date
            batch.purchase_price = purchase_price
            batch.selling_price = selling_price

            if mrp is not None:
                batch.mrp = mrp

        # -----------------------------------------------------
        # 6. Increase stock
        # -----------------------------------------------------

        batch.quantity += quantity
        batch.is_active = True

        batch.save(
            update_fields=[
                "manufacturing_date",
                "expiry_date",
                "purchase_price",
                "selling_price",
                "mrp",
                "quantity",
                "is_active",
                "updated_at",
            ]
        )

        # -----------------------------------------------------
        # 7. Calculate item total
        # -----------------------------------------------------

        item_total = (
            purchase_price * quantity
        )

        subtotal += item_total

        # -----------------------------------------------------
        # 8. Create PurchaseItem
        # -----------------------------------------------------

        PurchaseItem.objects.create(
            purchase=purchase,
            batch=batch,
            quantity=quantity,
            unit_price=purchase_price,
            total=item_total,
        )

        # -----------------------------------------------------
        # 9. Create StockTransaction
        # -----------------------------------------------------

        StockTransaction.objects.create(
            batch=batch,
            transaction_type=(
                StockTransaction.TransactionType.PURCHASE
            ),
            quantity=quantity,
            reference_id=purchase.id,
            notes=(
                f"Purchase invoice "
                f"{purchase.invoice_number}"
            ),
            created_by=created_by,
        )

    # ---------------------------------------------------------
    # 10. Calculate final purchase total
    # ---------------------------------------------------------

    total = subtotal - discount + tax

    if total < 0:
        raise ValueError(
            "Purchase total cannot be negative."
        )

    purchase.subtotal = subtotal
    purchase.total = total

    # Purchase is now completely processed.
    purchase.status = Purchase.Status.COMPLETED

    purchase.save(
        update_fields=[
            "subtotal",
            "total",
            "status",
            "updated_at",
        ]
    )

    return purchase