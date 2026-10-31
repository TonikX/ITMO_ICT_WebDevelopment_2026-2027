"""Корневые маршруты проекта django_project_vostrov (Практика 2)."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project_first_app.urls')),
]
