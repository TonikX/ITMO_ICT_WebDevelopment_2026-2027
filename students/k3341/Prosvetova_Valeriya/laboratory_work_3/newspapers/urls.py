from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('newspapers', views.NewspaperViewSet)
router.register('printing-houses', views.PrintingHouseViewSet)
router.register('post-offices', views.PostOfficeViewSet)
router.register('print-runs', views.PrintRunViewSet)
router.register('deliveries', views.DeliveryViewSet)

urlpatterns = [
    path('analytics/newspapers/<int:newspaper_id>/printing-addresses/', views.printing_addresses),
    path('analytics/printing-houses/<int:printing_house_id>/top-editor/', views.top_editor),
    path('analytics/post-offices-by-price/', views.post_offices_by_price),
    path('analytics/low-deliveries/', views.low_deliveries),
    path('analytics/newspapers/<int:newspaper_id>/destinations/', views.destinations),
    path('analytics/newspapers/<int:newspaper_id>/reference/', views.newspaper_reference),
    path('reports/printing-houses/', views.printing_houses_report),
] + router.urls
