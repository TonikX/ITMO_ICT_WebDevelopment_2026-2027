from django.urls import path
from . import views

urlpatterns = [
    path('owner/<int:owner_id>/', views.owner_by_id),
    path('owners/', views.list_owners),
    path('cars/', views.CarListView.as_view()),
    path('cars/<int:pk>/', views.CarDetailView.as_view()),
    path('create_owner/', views.create_car_owner),
    path('cars/create/', views.CarCreateView.as_view()),
    path('cars/<int:pk>/update/', views.CarUpdateView.as_view()),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view())
]