from rest_framework.routers import DefaultRouter

from .views import BillViewSet

app_name = "billing"

router = DefaultRouter()
router.register(r"", BillViewSet, basename="bill")

urlpatterns = router.urls
