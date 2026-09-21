from rest_framework import serializers

from apps.medicines.models import Medicine
from apps.suppliers.models import Supplier


class PurchaseItemInputSerializer(serializers.Serializer):
    medicine = serializers.PrimaryKeyRelatedField(
        queryset=Medicine.objects.filter(
            is_active=True
        )
    )

    batch_number = serializers.CharField(
        max_length=100
    )

    manufacturing_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    expiry_date = serializers.DateField()

    quantity = serializers.IntegerField(
        min_value=1
    )

    purchase_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    selling_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    mrp = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0,
    )

    def validate(self, attrs):
        purchase_price = attrs["purchase_price"]
        selling_price = attrs["selling_price"]
        mrp = attrs.get("mrp")

        if selling_price < purchase_price:
            raise serializers.ValidationError({
                "selling_price": (
                    "Selling price cannot be lower "
                    "than purchase price."
                )
            })

        if mrp is not None and selling_price > mrp:
            raise serializers.ValidationError({
                "selling_price": (
                    "Selling price cannot be greater "
                    "than MRP."
                )
            })

        return attrs


class PurchaseCreateSerializer(serializers.Serializer):
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(
            is_active=True
        )
    )

    invoice_number = serializers.CharField(
        max_length=100
    )

    purchase_date = serializers.DateField()

    items = PurchaseItemInputSerializer(
        many=True,
        allow_empty=False,
    )

    discount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=0,
        min_value=0,
    )

    tax = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=0,
        min_value=0,
    )