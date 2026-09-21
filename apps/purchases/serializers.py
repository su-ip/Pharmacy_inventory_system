from rest_framework import serializers

from apps.purchases.models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(
        source="batch.batch_number",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="batch.medicine.name",
        read_only=True,
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "purchase",
            "batch",
            "batch_number",
            "medicine_name",
            "quantity",
            "unit_price",
            "discount",
            "tax",
            "total",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "purchase",
            "batch_number",
            "medicine_name",
            "total",
            "created_at",
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(
        many=True,
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "invoice_number",
            "purchase_date",
            "subtotal",
            "discount",
            "tax",
            "total",
            "status",
            "created_by",
            "created_by_username",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "supplier_name",
            "subtotal",
            "discount",
            "tax",
            "total",
            "status",
            "created_by",
            "created_by_username",
            "items",
            "created_at",
            "updated_at",
        ]