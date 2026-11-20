from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from farm.views import (
    AnalyticsViewSet,
    BreedSeasonDietViewSet,
    BreedViewSet,
    CageViewSet,
    ChickenCageAssignmentViewSet,
    ChickenViewSet,
    ChickenWeightRecordViewSet,
    DietViewSet,
    EggProductionRecordViewSet,
    EmployeeCageAssignmentViewSet,
    EmployeeViewSet,
    EmploymentContractViewSet,
    WorkshopViewSet,
)


router = DefaultRouter()
router.register("workshops", WorkshopViewSet)
router.register("cages", CageViewSet)
router.register("breeds", BreedViewSet)
router.register("chickens", ChickenViewSet)
router.register("weights", ChickenWeightRecordViewSet)
router.register("chicken-cage-assignments", ChickenCageAssignmentViewSet)
router.register("employees", EmployeeViewSet)
router.register("contracts", EmploymentContractViewSet)
router.register("employee-cage-assignments", EmployeeCageAssignmentViewSet)
router.register("egg-records", EggProductionRecordViewSet)
router.register("diets", DietViewSet)
router.register("breed-season-diets", BreedSeasonDietViewSet)
router.register("analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("api/", include(router.urls)),
]
