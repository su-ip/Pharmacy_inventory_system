from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.models import Batch, StockTransaction
from apps.sales.models import Sale, SaleItem, Payment


@transaction.atomic
def create_sale(
    *,
    invoice_number,
    items,
    created_by,
    customer=None,
    discount=Decimal("0.00"),
    tax=Decimal("0.00"),
    payment_method=None,
    payment_amount=None,
    payment_reference="",
):
    """
    Create a sale using FEFO batch selection.

    items example:

    [
        {
            "medicine": medicine,
            "quantity": 30,
        }
    ]

    Django automatically selects batches according
    to earliest expiry date.
    """

    if not items:
        raise ValueError(
            "Sale must contain at least one item."
        )

    if discount < 0:
        raise ValueError(
            "Discount cannot be negative."
        )

    if tax < 0:
        raise ValueError(
            "Tax cannot be negative."
        )

    # ---------------------------------------------------------
    # 1. Create sale
    # ---------------------------------------------------------

    sale = Sale.objects.create(
        invoice_number=invoice_number,
        customer=customer,
        discount=discount,
        tax=tax,
        status=Sale.Status.COMPLETED,
        created_by=created_by,
    )

    subtotal = Decimal("0.00")

    # ---------------------------------------------------------
    # 2. Process each medicine
    # ---------------------------------------------------------

    for item in items:

        medicine = item["medicine"]
        requested_quantity = int(item["quantity"])

        if requested_quantity <= 0:
            raise ValueError(
                "Sale quantity must be greater than zero."
            )

        remaining_quantity = requested_quantity

        # -----------------------------------------------------
        # FEFO
        # -----------------------------------------------------

        batches = (
            Batch.objects
            .select_for_update()
            .filter(
                medicine=medicine,
                quantity__gt=0,
                expiry_date__gte=timezone.now().date(),
                is_active=True,
            )
            .order_by("expiry_date")
        )

        available_quantity = sum(
            batch.quantity for batch in batches
        )

        if available_quantity < requested_quantity:
            raise ValueError(
                f"Insufficient stock for {medicine}. "
                f"Available: {available_quantity}, "
                f"Requested: {requested_quantity}"
            )

        # -----------------------------------------------------
        # Consume batches using FEFO
        # -----------------------------------------------------

        for batch in batches:

            if remaining_quantity <= 0:
                break

            quantity_from_batch = min(
                batch.quantity,
                remaining_quantity
            )

            unit_price = batch.selling_price

            item_total = (
                unit_price * quantity_from_batch
            )

            # Reduce stock
            batch.quantity -= quantity_from_batch

            if batch.quantity == 0:
                batch.is_active = False

            batch.save(
                update_fields=[
                    "quantity",
                    "is_active",
                    "updated_at",
                ]
            )

            # Create sale item
            SaleItem.objects.create(
                sale=sale,
                batch=batch,
                quantity=quantity_from_batch,
                unit_price=unit_price,
                total=item_total,
            )

            # Create stock transaction
            StockTransaction.objects.create(
                batch=batch,
                transaction_type=(
                    StockTransaction.TransactionType.SALE
                ),
                quantity=quantity_from_batch,
                reference_id=sale.id,
                notes=(
                    f"Sale invoice "
                    f"{sale.invoice_number}"
                ),
                created_by=created_by,
            )

            subtotal += item_total

            remaining_quantity -= quantity_from_batch

    # ---------------------------------------------------------
    # 3. Calculate sale total
    # ---------------------------------------------------------

    total = subtotal - discount + tax

    if total < 0:
        raise ValueError(
            "Sale total cannot be negative."
        )

    sale.subtotal = subtotal
    sale.total = total

    sale.save(
        update_fields=[
            "subtotal",
            "total",
            "updated_at",
        ]
    )

    # ---------------------------------------------------------
    # 4. Record payment
    # ---------------------------------------------------------

    if payment_method is not None:

        if payment_amount is None:
            payment_amount = total

        payment_amount = Decimal(
            str(payment_amount)
        )

        if payment_amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        if payment_amount > total:
            raise ValueError(
                "Payment cannot exceed sale total."
            )

        Payment.objects.create(
            sale=sale,
            method=payment_method,
            amount=payment_amount,
            reference=payment_reference,
        )

    return sale