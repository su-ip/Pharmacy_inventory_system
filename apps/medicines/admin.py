from django.contrib import admin

from .models import Category, Manufacturer, Medicine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
    )


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
    )

    search_fields = (
        "name",
        "company_name",
    )


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "generic_name",
        "strength",
        "dosage_form",
        "category",
        "manufacturer",
        "barcode",
        "reorder_level",
        "is_active",
    )

    list_filter = (
        "dosage_form",
        "category",
        "manufacturer",
        "is_active",
    )

    search_fields = (
        "name",
        "generic_name",
        "brand_name",
        "barcode",
    )