from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('room/<int:room_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservations/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
    path('room/<int:room_id>/review/', views.create_review, name='create_review'),
    path('guests/', views.recent_guests, name='recent_guests'),
]