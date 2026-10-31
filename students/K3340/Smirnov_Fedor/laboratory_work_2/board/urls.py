from django.urls import path

from . import views

urlpatterns = [
    path('', views.board, name='board'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('flights/<int:pk>/', views.flight_page, name='flight'),
    path('flights/<int:pk>/book/', views.book_seat, name='book_seat'),
    path('flights/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/change/', views.change_booking, name='change_booking'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:pk>/check-in/', views.check_in, name='check_in'),
]
