from django_filters.rest_framework import (
    DjangoFilterBackend,
)
from rest_framework import viewsets
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)

from apps.inventory.models import (
    Batch,
    StockTransaction,
)
from apps.inventory.permissions import (
    InventoryPermission,
    StockTransactionPermission,
)
from apps.inventory.serializers import (
    BatchSerializer,
    StockTransactionSerializer,
)


class BatchViewSet(viewsets.ModelViewSet):

    queryset = Batch.objects.select_related(
        "medicine",
    ).all()

    serializer_class = BatchSerializer
    permission_classes = [InventoryPermission]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "medicine",
        "is_active",
    ]

    search_fields = [
        "batch_number",
        "medicine__name",
        "medicine__generic_name",
        "medicine__brand_name",
        "medicine__barcode",
    ]

    ordering_fields = [
        "expiry_date",
        "quantity",
        "purchase_price",
        "selling_price",
        "created_at",
    ]

    ordering = [
        "expiry_date",
    ]


class StockTransactionViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = StockTransaction.objects.select_related(
        "batch",
        "batch__medicine",
        "created_by",
    ).all()

    serializer_class = StockTransactionSerializer
    permission_classes = [
        StockTransactionPermission
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "batch",
        "transaction_type",
        "created_by",
    ]

    search_fields = [
        "batch__batch_number",
        "batch__medicine__name",
        "notes",
    ]

    ordering_fields = [
        "created_at",
        "quantity",
        "transaction_type",
    ]

    ordering = [
        "-created_at",
    ]