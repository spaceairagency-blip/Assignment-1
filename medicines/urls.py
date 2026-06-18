from rest_framework.routers import DefaultRouter

from .views import MedicineViewSet

app_name = "medicines"

router = DefaultRouter()
router.register(r"", MedicineViewSet, basename="medicine")

urlpatterns = router.urls
