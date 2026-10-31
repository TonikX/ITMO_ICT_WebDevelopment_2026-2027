"""Маршруты приложения "Автовладельцы" (Практика 1).

Задание 5: адрес вида /owner/<id>/ показывает данные владельца.
Ожидаемый результат: http://127.0.0.1:8000/owner/1 — первый владелец.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('owner/<int:pk>/', views.owner, name='owner'),
]
