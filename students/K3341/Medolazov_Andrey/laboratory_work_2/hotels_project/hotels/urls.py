from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotels/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/reserve/', views.reservation_create, name='reservation_create'),
    path('rooms/<int:room_id>/review/', views.review_create, name='review_create'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:pk>/edit/', views.reservation_edit, name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.reservation_delete, name='reservation_delete'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('guests/', views.guests, name='guests'),
    path('manage/', views.manage_reservations, name='manage_reservations'),
    path('manage/<int:pk>/<str:action>/', views.change_status, name='change_status'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
