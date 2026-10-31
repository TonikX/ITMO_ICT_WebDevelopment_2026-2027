from django.urls import path
from . import views

urlpatterns = [
    path('', views.HotelListView.as_view(), name='hotel_list'),
    path('hotel/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:pk>/update/', views.booking_update, name='booking_update'),
    path('booking/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('guests/', views.guests_table, name='guests_table'),
    path('hotel/create/', views.hotel_create, name='hotel_create'),
    path('hotel/<int:pk>/update/', views.hotel_update, name='hotel_update'),
    path('hotel/<int:pk>/delete/', views.hotel_delete, name='hotel_delete'),
    path('hotel/<int:hotel_pk>/room/create/', views.room_create, name='room_create'),
    path('all-bookings/', views.all_bookings, name='all_bookings'),
]