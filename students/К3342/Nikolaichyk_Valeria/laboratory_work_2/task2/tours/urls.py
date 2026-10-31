from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('register/', views.register, name='register'),
    path('tour/<int:tour_id>/book/',views.book_tour,name='book_tour'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/edit/',views.edit_booking,name='edit_booking'),
    path('booking/<int:booking_id>/delete/',views.delete_booking, name='delete_booking'),
    path('tour/<int:tour_id>/review/add/', views.add_review, name='add_review'),
    path( 'manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('booking/<int:booking_id>/confirm/',views.confirm_booking,name='confirm_booking'),
    path('sales-statistics/', views.sales_statistics,name='sales_statistics'),
]