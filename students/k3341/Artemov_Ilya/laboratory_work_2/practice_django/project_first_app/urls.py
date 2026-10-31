from django.urls import path
from . import views

urlpatterns = [
    path("", views.owner_list, name="owners"),
    path("owners/", views.owner_list, name="owner_list"),
    path("owner/create/", views.owner_create, name="owner_create"),
    path("owner/<int:owner_id>/", views.owner_detail, name="owner"),
    path("cars/", views.CarListView.as_view(), name="cars"),
    path("car/create/", views.CarCreateView.as_view(), name="car_create"),
    path("car/<int:pk>/", views.CarDetailView.as_view(), name="car"),
    path("car/<int:pk>/update/", views.CarUpdateView.as_view(), name="car_update"),
    path("car/<int:pk>/delete/", views.CarDeleteView.as_view(), name="car_delete"),
]
