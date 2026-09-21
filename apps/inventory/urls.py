from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inventory.stock_views import StockAdjustmentView
from apps.inventory.views import (
    BatchViewSet,
    StockTransactionViewSet,
)


router = DefaultRouter()

router.register(
    r"batches",
    BatchViewSet,
    basename="batch",
)

router.register(
    r"stock-transactions",
    StockTransactionViewSet,
    basename="stock-transaction",
)

urlpatterns = [
    path(
        "stock/adjust/",
        StockAdjustmentView.as_view(),
        name="stock-adjust",
    ),
]

urlpatterns += router.urls