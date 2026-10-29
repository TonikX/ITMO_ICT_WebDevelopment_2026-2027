from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('rooms/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/review/', views.review_create, name='review_create'),
    path('staff/bookings/', views.staff_bookings, name='staff_bookings'),
    path('staff/bookings/<int:pk>/<str:action>/', views.staff_action, name='staff_action'),
    path('staff/guests/', views.guests, name='guests'),
]
