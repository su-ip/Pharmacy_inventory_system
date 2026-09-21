from django.contrib import admin

from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = (
        "total",
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "supplier",
        "purchase_date",
        "subtotal",
        "discount",
        "tax",
        "total",
        "status",
        "created_by",
    )

    list_filter = (
        "status",
        "purchase_date",
    )

    search_fields = (
        "invoice_number",
        "supplier__name",
        "supplier__company_name",
    )

    inlines = [
        PurchaseItemInline,
    ]