from django.urls import path

from . import views

urlpatterns = [
    path("", views.owner_list, name="home"),
    path("auth/", views.auth_page, name="auth"),
    path("logout/", views.logout_view, name="logout"),
    path("owners/register/", views.auth_page, name="owner_register"),
    path("owner/<int:owner_id>/", views.owner_detail, name="owner_detail"),
    path("owners/", views.owner_list, name="owner_list"),
    path("owners/create/", views.owner_create, name="owner_create"),
    path("cars/", views.CarListView.as_view(), name="car_list"),
    path("cars/<int:pk>/", views.CarDetailView.as_view(), name="car_detail"),
    path("cars/create/", views.CarCreateView.as_view(), name="car_create"),
    path(
        "cars/<int:pk>/update/",
        views.CarUpdateView.as_view(),
        name="car_update",
    ),
    path(
        "cars/<int:pk>/delete/",
        views.CarDeleteView.as_view(),
        name="car_delete",
    ),
]
