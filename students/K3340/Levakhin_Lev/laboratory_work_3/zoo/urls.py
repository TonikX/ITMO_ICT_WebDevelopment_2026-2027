from django.urls import path
from rest_framework import serializers
from rest_framework.routers import SimpleRouter

from . import models, views
from . import serializers as schema

router = SimpleRouter()
router.register("animals", views.AnimalViewSet)
router.register("leases", views.LeaseViewSet)

resources = {
    "zoos": (models.Zoo, schema.ZooSerializer),
    "habitat-zones": (models.HabitatZone, None),
    "species": (models.Species, schema.SpeciesSerializer),
    "departments": (models.Department, schema.DepartmentSerializer),
    "buildings": (models.Building, schema.BuildingSerializer),
    "enclosures": (models.Enclosure, schema.EnclosureSerializer),
    "employees": (models.Employee, schema.EmployeeSerializer),
    "care-assignments": (models.CareAssignment, None),
    "bird-winterings": (models.BirdWintering, schema.BirdWinteringSerializer),
    "reptile-hibernations": (models.ReptileHibernation, schema.ReptileHibernationSerializer),
    "diets": (models.Diet, None),
    "diet-assignments": (models.DietAssignment, schema.DietAssignmentSerializer),
}

for route, (model, serializer) in resources.items():
    if serializer is None:
        meta = type("Meta", (), {"model": model, "fields": "__all__"})
        serializer = type(f"{model.__name__}Serializer", (schema.CheckedSerializer,), {"Meta": meta})
    queryset = model.objects.order_by("id")
    if model is models.Department:
        queryset = queryset.prefetch_related("enclosures")
    viewset = type(f"{model.__name__}ViewSet", (views.ZooViewSet,), {
        "queryset": queryset,
        "serializer_class": serializer,
    })
    router.register(route, viewset, basename=route)

urlpatterns = router.urls + [
    path("reports/department-counts/", views.department_counts),
    path("reports/shared-enclosures/", views.shared_enclosure_animals),
    path("reports/empty-enclosures/", views.empty_enclosures),
    path("reports/incoming-leases/", views.incoming_leases),
    path("reports/outgoing-leases/", views.outgoing_report),
]
