from django.urls import path
from . import views as v
urlpatterns=[path('owners/',v.owners,name='owners'),path('owners/new/',v.owner_create,name='owner_create'),
 path('owner/<int:pk>/',v.owner_detail,name='owner_detail'),path('cars/',v.CarList.as_view(),name='cars'),
 path('cars/new/',v.CarCreate.as_view(),name='car_create'),path('cars/<int:pk>/',v.CarDetail.as_view(),name='car_detail'),
 path('cars/<int:pk>/edit/',v.CarUpdate.as_view(),name='car_edit'),path('cars/<int:pk>/delete/',v.CarDelete.as_view(),name='car_delete')]
