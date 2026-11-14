from django.urls import path
from . import views  # Здесь этот импорт сработает правильно!
from .views import CarListView, CarUpdateView, CarCreate, CarDelete

urlpatterns = [
    # Ваши текущие маршруты приложения (если они есть)
    path('owners/owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('owners/', views.owners_list, name='owners_list'),
    path('owners/create_owner/', views.create_owner, name='owner_create'),
    path('owners/<int:pk>/update/', views.owner_update, name='owner_update'),
    path('owners/<int:pk>/delete/', views.owner_delete, name='owner_delete'),
    path('cars/', views.CarListView.as_view(), name='cars_list'),
    path('cars/car/<int:pk>', views.CarDetailView.as_view(), name = 'car_detail'),
    path('cars/<int:pk>/update/', CarUpdateView.as_view(), name='car_update'),
    path('cars/create/', CarCreate.as_view(), name = 'car_create'),
    path('cars/<int:pk>/delete/', CarDelete.as_view(), name = 'car_delete'),

]

