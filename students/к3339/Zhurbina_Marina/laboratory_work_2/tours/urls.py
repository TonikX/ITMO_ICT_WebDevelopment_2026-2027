from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.TourListView.as_view(), name='tour_list'),
    path('tours/<int:pk>/', views.TourDetailView.as_view(), name='tour_detail'),
    path('tours/<int:pk>/reserve/', views.tour_reserve, name='tour_reserve'),

    path('my-reservations/', views.MyReservationsView.as_view(), name='my_reservations'),
    path('reservations/<int:pk>/edit/', views.ReservationUpdateView.as_view(),
         name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.ReservationDeleteView.as_view(),
         name='reservation_delete'),
    path('sales/', views.sales, name='sales'),

    path('register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='tours/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
