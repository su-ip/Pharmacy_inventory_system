from rest_framework import serializers

from apps.inventory.models import Batch, StockTransaction


class BatchSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    medicine_generic_name = serializers.CharField(
        source="medicine.generic_name",
        read_only=True,
    )

    dosage_form = serializers.CharField(
        source="medicine.dosage_form",
        read_only=True,
    )

    class Meta:
        model = Batch

        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_generic_name",
            "dosage_form",
            "batch_number",
            "manufacturing_date",
            "expiry_date",
            "purchase_price",
            "selling_price",
            "mrp",
            "quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "medicine_name",
            "medicine_generic_name",
            "dosage_form",
            "quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        purchase_price = attrs.get(
            "purchase_price",
            getattr(self.instance, "purchase_price", None),
        )

        selling_price = attrs.get(
            "selling_price",
            getattr(self.instance, "selling_price", None),
        )

        mrp = attrs.get(
            "mrp",
            getattr(self.instance, "mrp", None),
        )

        expiry_date = attrs.get(
            "expiry_date",
            getattr(self.instance, "expiry_date", None),
        )

        if selling_price is not None and purchase_price is not None:
            if selling_price < purchase_price:
                raise serializers.ValidationError({
                    "selling_price": (
                        "Selling price cannot be lower "
                        "than purchase price."
                    )
                })

        if mrp is not None and selling_price is not None:
            if selling_price > mrp:
                raise serializers.ValidationError({
                    "selling_price": (
                        "Selling price cannot be greater "
                        "than MRP."
                    )
                })

        from django.utils import timezone

        if expiry_date and expiry_date < timezone.now().date():
            raise serializers.ValidationError({
                "expiry_date": (
                    "A batch cannot have an expiry date "
                    "in the past."
                )
            })

        return attrs


class StockTransactionSerializer(
    serializers.ModelSerializer
):
    medicine_name = serializers.CharField(
        source="batch.medicine.name",
        read_only=True,
    )

    batch_number = serializers.CharField(
        source="batch.batch_number",
        read_only=True,
    )

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = StockTransaction

        fields = [
            "id",
            "batch",
            "batch_number",
            "medicine_name",
            "transaction_type",
            "transaction_type_display",
            "quantity",
            "reference_id",
            "notes",
            "created_by",
            "created_by_username",
            "created_at",
        ]

        read_only_fields = fields