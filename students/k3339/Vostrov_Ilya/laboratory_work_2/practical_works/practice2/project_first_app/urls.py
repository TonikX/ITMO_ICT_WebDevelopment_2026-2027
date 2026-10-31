"""Маршруты приложения "Автовладельцы" (Практическое занятие 2).

- FBV: /owners/ (все владельцы), /owner/create/ (форма владельца),
       /owner/<id>/ (владелец, из практики 1);
- CBV: /cars/, /cars/<pk>/, /cars/<pk>/update/, /cars/create/, /cars/<pk>/delete/.
CBV подключаются через as_view(), параметр — <int:pk>.
"""

from django.urls import path

from . import views

urlpatterns = [
    # FBV (задание 2, задание 3)
    path('owners/', views.get_all_owners, name='owners_list'),
    path('owner/<int:pk>/', views.owner, name='owner'),
    path('owner/create/', views.create_owner, name='create_owner'),

    # CBV (задание 2: список/детали/обновление; задание 3: создание/удаление)
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/update/', views.CarUpdateView.as_view(), name='car_update'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]
