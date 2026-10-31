from django.urls import path

from . import views


urlpatterns = [
    path("", views.TourListView.as_view(), name="tour_list"),
    path("register/", views.register, name="register"),
    path("tours/<int:pk>/", views.TourDetailView.as_view(), name="tour_detail"),
    path("tours/<int:tour_id>/reserve/", views.reserve_tour, name="reserve_tour"),
    path(
        "tours/<int:tour_id>/reviews/create/",
        views.ReviewCreateView.as_view(),
        name="review_create",
    ),
    path("reservations/", views.ReservationListView.as_view(), name="reservation_list"),
    path(
        "reservations/<int:pk>/edit/",
        views.ReservationUpdateView.as_view(),
        name="reservation_update",
    ),
    path(
        "reservations/<int:pk>/delete/",
        views.ReservationDeleteView.as_view(),
        name="reservation_delete",
    ),
    path(
        "reservations/<int:pk>/confirm/",
        views.confirm_reservation,
        name="reservation_confirm",
    ),
    path("sold-tours/", views.SoldTourListView.as_view(), name="sold_tour_list"),
]
