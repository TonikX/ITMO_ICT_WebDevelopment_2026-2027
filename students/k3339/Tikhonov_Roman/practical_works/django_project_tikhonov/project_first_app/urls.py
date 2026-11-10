from django.urls import path

from . import views

urlpatterns = [
    path("owners/", views.owner_list),
    path("owners/create/", views.owner_create),
    path("owner/<int:owner_id>/", views.owner_detail),
    path("cars/", views.CarListView.as_view()),
    path("cars/create/", views.CarCreateView.as_view()),
    path("cars/<int:pk>/", views.CarDetailView.as_view()),
    path("cars/<int:pk>/update/", views.CarUpdateView.as_view()),
    path("cars/<int:pk>/delete/", views.CarDeleteView.as_view()),
]
