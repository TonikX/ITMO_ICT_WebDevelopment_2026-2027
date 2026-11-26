# urls.py приложения
from django.urls import path
from . import views

urlpatterns = [
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('driver/create/', views.create_driver),
    path('driver/', views.drivers_info, name='driver_list'),
    path('car/', views.CarListView.as_view(), name='car_list'),
    path('car/<int:pk>/', views.CarSingleView.as_view()),
    path('car/<int:pk>/edit', views.CarUpdateView.as_view(), name='car_update'),
    path('car/create/', views.CarCreateForm.as_view()),
    path('car/<int:pk>/update/', views.CarUpdateForm.as_view()),
    path('car/<int:pk>/delete/', views.CarDeleteForm.as_view()),
]