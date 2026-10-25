from django.urls import path
from . import views

urlpatterns = [
    path('', views.tour_list, name='tour_list'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),
    path('tour/<int:pk>/book/', views.book_tour, name='book_tour'),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:pk>/delete/", views.delete_booking, name="delete_booking"),
    path("booking/<int:pk>/edit/", views.edit_booking, name="edit_booking"),
    path("register/", views.register, name="register"),
    path("tour/<int:pk>/review/", views.add_review,name="add_review"),
    path('sales/', views.sales_by_country, name='sales_by_country'),
]

