from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.inventory.models import Batch, StockTransaction
from apps.inventory.services.stock_service import adjust_stock


class StockAdjustmentSerializer(serializers.Serializer):
    batch = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    transaction_type = serializers.ChoiceField(
        choices=[
            choice[0]
            for choice in StockTransaction.TransactionType.choices
            if choice[0] in {
                StockTransaction.TransactionType.DAMAGE,
                StockTransaction.TransactionType.EXPIRED,
                StockTransaction.TransactionType.ADJUSTMENT_IN,
                StockTransaction.TransactionType.ADJUSTMENT_OUT,
            }
        ]
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class StockAdjustmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_superuser:
            allowed = True
        else:
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                return Response(
                    {"detail": "User profile not found."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            allowed = (
                profile.is_active
                and profile.role in {
                    UserProfile.Role.ADMIN,
                    UserProfile.Role.PHARMACIST,
                    UserProfile.Role.STOREKEEPER,
                }
            )

        if not allowed:
            return Response(
                {"detail": "You do not have permission to adjust stock."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StockAdjustmentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            batch = Batch.objects.get(
                pk=serializer.validated_data["batch"]
            )
        except Batch.DoesNotExist:
            return Response(
                {"detail": "Batch not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            transaction_record = adjust_stock(
                batch=batch,
                quantity=serializer.validated_data["quantity"],
                transaction_type=(
                    serializer.validated_data["transaction_type"]
                ),
                created_by=request.user,
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Stock adjusted successfully.",
                "transaction_id": str(
                    transaction_record.id
                ),
                "batch_id": str(batch.id),
            },
            status=status.HTTP_200_OK,
        )