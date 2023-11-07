from django.conf import settings
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter, SimpleRouter

from app.fish.views import FishViewSet, FishVariantViewSet, DiscountViewSet
from app.logistics.views import RecordViewSet, BillViewSet, BillItemViewSet, StockViewSet, ExpenseViewSet
from app.organizations.views import OrganizationViewSet, PlaceViewSet, ExpenseTypeViewSet
from app.users.views import OtpLoginViewSet, UserViewSet, AuthenticationViewSet
from app.utils.views import get_enum_values

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename='users')
router.register("otp", OtpLoginViewSet, basename='otp')
router.register("authentication", AuthenticationViewSet, basename='authentication')
router.register("fish", FishViewSet, basename='fish')
router.register("fish-variants", FishVariantViewSet, basename='fish-variants')
router.register("discounts", DiscountViewSet, basename='discounts')
router.register("records", RecordViewSet, basename='records')
router.register("bills", BillViewSet, basename='bills')
router.register("bill-items", BillItemViewSet, basename='bill-items')
router.register("stocks", StockViewSet, basename='stocks')
router.register("expenses", ExpenseViewSet, basename='expenses')
router.register("organizations", OrganizationViewSet, basename='organizations')
router.register("places", PlaceViewSet, basename='places')
router.register("expense-types", ExpenseTypeViewSet, basename='expense-types')


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path('get-enum-values/', get_enum_values, name='get_enum_values'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]
