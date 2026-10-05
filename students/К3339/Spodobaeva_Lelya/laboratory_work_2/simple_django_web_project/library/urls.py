from django.urls import path

from . import views


urlpatterns = [
    path("", views.tour_list, name="tour_list"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("my-reservations/", views.my_reservations, name="my_reservations"),
    path("admin-reservations/", views.admin_reservations, name="admin_reservations"),
    path(
        "admin-reservations/<int:reservation_id>/confirm/",
        views.confirm_reservation,
        name="confirm_reservation",
    ),
    path("sold-by-country/", views.sold_by_country, name="sold_by_country"),
    path("tours/<int:tour_id>/", views.tour_detail, name="tour_detail"),
    path("tours/<int:tour_id>/reserve/", views.reserve_tour, name="reserve_tour"),
    path("tours/<int:tour_id>/review/", views.add_review, name="add_review"),
    path("reservations/<int:reservation_id>/edit/", views.edit_reservation, name="edit_reservation"),
    path("reservations/<int:reservation_id>/delete/", views.delete_reservation, name="delete_reservation"),
]
