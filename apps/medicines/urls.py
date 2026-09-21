from rest_framework.routers import DefaultRouter

from apps.medicines.views import (
    CategoryViewSet,
    ManufacturerViewSet,
    MedicineViewSet,
)


router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    r"manufacturers",
    ManufacturerViewSet,
    basename="manufacturer",
)

router.register(
    r"medicines",
    MedicineViewSet,
    basename="medicine",
)

urlpatterns = router.urls