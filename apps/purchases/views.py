from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.purchases.input_serializers import (
    PurchaseCreateSerializer,
)
from apps.purchases.models import Purchase
from apps.purchases.permissions import PurchasePermission
from apps.purchases.serializers import PurchaseSerializer
from apps.purchases.services.purchase_service import (
    create_purchase,
)


class PurchaseViewSet(viewsets.ModelViewSet):

    queryset = Purchase.objects.select_related(
        "supplier",
        "created_by",
    ).prefetch_related(
        "items__batch__medicine",
    )

    permission_classes = [
        PurchasePermission,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "supplier",
        "status",
    ]

    search_fields = [
        "invoice_number",
        "supplier__name",
        "supplier__company_name",
    ]

    ordering_fields = [
        "purchase_date",
        "total",
        "created_at",
    ]

    ordering = [
        "-purchase_date",
        "-created_at",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseCreateSerializer

        return PurchaseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:
            purchase = create_purchase(
                supplier=data["supplier"],
                invoice_number=data["invoice_number"],
                purchase_date=data["purchase_date"],
                items=data["items"],
                created_by=request.user,
                discount=data.get(
                    "discount",
                    0,
                ),
                tax=data.get(
                    "tax",
                    0,
                ),
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = PurchaseSerializer(
            purchase,
            context={
                "request": request
            },
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        purchase = self.get_object()

        if purchase.status == Purchase.Status.COMPLETED:
            return Response(
                {
                    "detail": (
                        "Completed purchases cannot be "
                        "deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase.status = Purchase.Status.CANCELLED

        purchase.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Purchase cancelled successfully."
                )
            },
            status=status.HTTP_200_OK,
        )