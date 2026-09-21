from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.medicines.models import Category, Manufacturer, Medicine
from apps.medicines.permissions import MedicinePermission
from apps.medicines.serializers import (
    CategorySerializer,
    ManufacturerSerializer,
    MedicineSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [MedicinePermission]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = ["name"]


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [MedicinePermission]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "address",
        "phone",
        "email",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = ["name"]


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related(
        "category",
        "manufacturer",
    ).all()

    serializer_class = MedicineSerializer
    permission_classes = [MedicinePermission]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "category",
        "manufacturer",
        "dosage_form",
        "is_active",
    ]

    search_fields = [
        "name",
        "generic_name",
        "brand_name",
        "strength",
        "barcode",
    ]

    ordering_fields = [
        "name",
        "generic_name",
        "created_at",
        "updated_at",
    ]

    ordering = ["name"]

    def destroy(self, request, *args, **kwargs):
        """
        Do not physically delete medicines.

        Medicines are deactivated instead so historical
        purchases and sales remain safe.
        """

        medicine = self.get_object()

        medicine.is_active = False
        medicine.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "Medicine deactivated successfully."
            },
            status=status.HTTP_200_OK,
        )