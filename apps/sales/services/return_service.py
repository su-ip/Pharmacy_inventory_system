from django.db import transaction

from apps.inventory.models import StockTransaction
from apps.inventory.services.stock_service import adjust_stock
from apps.sales.models import Sale, SaleItem


@transaction.atomic
def return_sale_item(
    *,
    sale_item,
    quantity,
    created_by,
    notes="",
):
    """
    Return a quantity from a previously completed sale.

    Returned quantity is added back to the original batch.
    """

    if sale_item.sale.status != Sale.Status.COMPLETED:
        raise ValueError(
            "Only completed sales can be returned."
        )

    if quantity <= 0:
        raise ValueError(
            "Return quantity must be greater than zero."
        )

    # ---------------------------------------------------------
    # Check previous returns
    # ---------------------------------------------------------

    previous_returns = (
        StockTransaction.objects
        .filter(
            reference_id=sale_item.sale.id,
            batch=sale_item.batch,
            transaction_type=(
                StockTransaction.TransactionType.SALES_RETURN
            ),
        )
        .values_list("quantity", flat=True)
    )

    returned_quantity = sum(
        previous_returns
    )

    remaining_returnable = (
        sale_item.quantity - returned_quantity
    )

    if quantity > remaining_returnable:
        raise ValueError(
            f"Cannot return {quantity} units. "
            f"Only {remaining_returnable} units "
            f"are returnable."
        )

    # ---------------------------------------------------------
    # Add stock back
    # ---------------------------------------------------------

    transaction_record = adjust_stock(
        batch=sale_item.batch,
        quantity=quantity,
        transaction_type=(
            StockTransaction.TransactionType.SALES_RETURN
        ),
        created_by=created_by,
        reference_id=sale_item.sale.id,
        notes=notes or (
            f"Return from sale "
            f"{sale_item.sale.invoice_number}"
        ),
    )

    return transaction_record