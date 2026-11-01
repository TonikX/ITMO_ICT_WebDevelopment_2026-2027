from django.urls import path

from . import views

urlpatterns = [
    path("", views.owner_list, name="owners"),
    path("owners/new/", views.owner_create, name="owner_create"),
    path("owner/<int:owner_id>/", views.owner_detail, name="owner_detail"),
    path("cars/", views.CarListView.as_view(), name="cars"),
    path("cars/new/", views.CarCreateView.as_view(), name="car_create"),
    path("cars/<int:pk>/", views.CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/edit/", views.CarUpdateView.as_view(), name="car_update"),
    path("cars/<int:pk>/delete/", views.CarDeleteView.as_view(), name="car_delete"),
]
