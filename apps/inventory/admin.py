from django.contrib import admin

from .models import Batch, StockTransaction


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):

    list_display = (
        "medicine",
        "batch_number",
        "expiry_date",
        "purchase_price",
        "selling_price",
        "quantity",
        "is_active",
    )

    list_filter = (
        "is_active",
        "expiry_date",
    )

    search_fields = (
        "medicine__name",
        "batch_number",
    )


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "batch",
        "transaction_type",
        "quantity",
        "created_by",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "batch__batch_number",
        "batch__medicine__name",
        "notes",
    )

    readonly_fields = (
        "id",
        "created_at",
    )