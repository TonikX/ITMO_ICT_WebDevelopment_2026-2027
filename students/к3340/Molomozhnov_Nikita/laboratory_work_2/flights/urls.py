from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.FlightListView.as_view(), name='flight_list'),
    path('flights/<int:pk>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('flights/<int:pk>/reserve/', views.ReservationCreateView.as_view(), name='reserve'),
    path('reservations/<int:pk>/update/', views.ReservationUpdateView.as_view(), name='reservation_update'),
    path('reservations/<int:pk>/delete/', views.ReservationDeleteView.as_view(), name='reservation_delete'),
    path('flights/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='flights/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]