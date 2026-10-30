from django.urls import path
from . import views


urlpatterns = [
    path('tours/register/', views.register_tours, name='register_tours'),
    path('tours/profile/', views.profile_tours, name='profile_tours'),
    path('tours/', views.TourListView.as_view(), name='tour_list'),
    path('tours/<int:pk>/', views.TourDetailView.as_view(), name='tour_detail'),

    path('tours/<int:pk>/reserve/', views.reserve_tour, name='reserve_tour'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservations/<int:pk>/update/', views.ReservationUpdateView.as_view(), name='reservation_update'),
    path('reservations/<int:pk>/delete/', views.ReservationDeleteView.as_view(), name='reservation_delete'),

    path('tours/<int:pk>/review/', views.add_review, name='add_review'),

    path('tours/create/', views.TourCreateView.as_view(), name='tour_create'),
    path('tours/<int:pk>/update/', views.TourUpdateView.as_view(), name='tour_update'),
    path('tours/<int:pk>/delete/', views.TourDeleteView.as_view(), name='tour_delete'),

    path('sold-tours/', views.SoldToursByCountryView.as_view(), name='sold_tours'),
]