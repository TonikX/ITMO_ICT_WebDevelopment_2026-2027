from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('owners/', views.owner_list, name='owner_list'),
    path('automobiles/',views.AutomobileListView.as_view(),name='automobile_list'),
    path('owner/create/', views.owner_create, name='owner_create'),
    path('automobile/create/',views.AutomobileCreateView.as_view(),name='automobile_create'),
]