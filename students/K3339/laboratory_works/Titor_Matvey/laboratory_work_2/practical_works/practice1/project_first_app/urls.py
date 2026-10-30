
from django.urls import path

from . import views

urlpatterns = [
    path('owner/<int:pk>/', views.owner, name='owner'),
]
