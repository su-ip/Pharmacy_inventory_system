from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company_name",
        "phone",
        "email",
        "pan_vat",
        "credit_limit",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "company_name",
        "phone",
        "pan_vat",
    )