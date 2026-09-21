from django.db import transaction
from django.utils import timezone

from apps.inventory.models import Batch, StockTransaction


INCREASE_TRANSACTION_TYPES = {
    StockTransaction.TransactionType.PURCHASE,
    StockTransaction.TransactionType.SALES_RETURN,
    StockTransaction.TransactionType.ADJUSTMENT_IN,
}

DECREASE_TRANSACTION_TYPES = {
    StockTransaction.TransactionType.SALE,
    StockTransaction.TransactionType.PURCHASE_RETURN,
    StockTransaction.TransactionType.DAMAGE,
    StockTransaction.TransactionType.EXPIRED,
    StockTransaction.TransactionType.ADJUSTMENT_OUT,
}


@transaction.atomic
def adjust_stock(
    *,
    batch,
    quantity,
    transaction_type,
    created_by,
    notes="",
    reference_id=None,
):
    """
    Safely increase or decrease stock.

    Quantity is always positive.

    The transaction type determines the direction.
    """

    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than zero."
        )

    if (
        transaction_type not in INCREASE_TRANSACTION_TYPES
        and transaction_type not in DECREASE_TRANSACTION_TYPES
    ):
        raise ValueError(
            f"Unsupported stock transaction type: "
            f"{transaction_type}"
        )

    # Lock the batch to prevent concurrent stock changes.
    batch = (
        Batch.objects
        .select_for_update()
        .get(pk=batch.pk)
    )

    if transaction_type in DECREASE_TRANSACTION_TYPES:

        if batch.quantity < quantity:
            raise ValueError(
                f"Insufficient stock for {batch}. "
                f"Available: {batch.quantity}, "
                f"Requested: {quantity}"
            )

        batch.quantity -= quantity

    else:
        batch.quantity += quantity

    # A batch with stock is active.
    # A batch with zero stock is inactive.
    batch.is_active = batch.quantity > 0

    batch.save(
        update_fields=[
            "quantity",
            "is_active",
            "updated_at",
        ]
    )

    transaction_record = StockTransaction.objects.create(
        batch=batch,
        transaction_type=transaction_type,
        quantity=quantity,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by,
    )

    return transaction_record