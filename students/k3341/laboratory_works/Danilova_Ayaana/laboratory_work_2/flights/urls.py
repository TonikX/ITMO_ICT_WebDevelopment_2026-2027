# Путь: flights/urls.py
# Не забудьте подключить эти urls в основном config/urls.py через include('flights.urls')

from django.urls import path
from . import views

app_name = 'flights'
urlpatterns = [
    path('register/', views.sign_up, name='register'),
    path('', views.FlightListView.as_view(), name='flight_list'),
    path('<uuid:pk>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('passengers/new/', views.passenger_create, name='passenger_create'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('<uuid:flight_id>/reserve/', views.reservation_create, name='reservation_create'),
    path(
        "reservations/<uuid:pk>/update/",
        views.ReservationUpdateView.as_view(),
        name="reservation_update",
    ),
    path(
        "reservations/<uuid:pk>/delete/",
        views.ReservationDeleteView.as_view(),
        name="reservation_delete",
    ),
    path("<uuid:flight_id>/review/", views.review_create, name="review_create"),
    path(
        "tickets/<uuid:ticket_id>/check-in/",
        views.staff_ticket_checkin,
        name="staff_ticket_checkin",
    ),
]
