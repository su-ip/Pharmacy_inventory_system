from rest_framework import serializers

from apps.medicines.models import Category, Manufacturer, Medicine


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = [
            "id",
            "name",
            "address",
            "phone",
            "email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class MedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    manufacturer_name = serializers.CharField(
        source="manufacturer.name",
        read_only=True,
    )

    class Meta:
        model = Medicine
        fields = [
            "id",
            "name",
            "generic_name",
            "brand_name",
            "strength",
            "dosage_form",
            "category",
            "category_name",
            "manufacturer",
            "manufacturer_name",
            "barcode",
            "reorder_level",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "category_name",
            "manufacturer_name",
        ]

    def validate_barcode(self, value):
        if value == "":
            return None

        return value