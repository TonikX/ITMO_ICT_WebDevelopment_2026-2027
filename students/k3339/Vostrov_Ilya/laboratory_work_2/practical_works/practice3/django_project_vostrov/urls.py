"""Корневые маршруты проекта django_project_vostrov (Практика 3)."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
    path('', include('project_first_app.urls')),
]
