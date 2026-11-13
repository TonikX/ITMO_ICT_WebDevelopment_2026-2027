from django.urls import path
from . import views as v
urlpatterns = [path('',v.TourList.as_view(),name='tour_list'),
 path('tours/new/',v.TourCreate.as_view(),name='tour_create'),
 path('tours/<int:pk>/',v.TourDetail.as_view(),name='tour_detail'),
 path('tours/<int:pk>/edit/',v.TourUpdate.as_view(),name='tour_edit'),
 path('tours/<int:pk>/book/',v.book,name='book'),
 path('tours/<int:pk>/review/',v.review_create,name='review_create'),
 path('bookings/',v.booking_list,name='my_bookings'),
 path('bookings/<int:pk>/edit/',v.booking_edit,name='booking_edit'),
 path('bookings/<int:pk>/delete/',v.booking_delete,name='booking_delete'),
 path('manage/bookings/',v.staff_bookings,name='staff_bookings'),
 path('manage/bookings/<int:pk>/confirm/',v.booking_confirm,name='booking_confirm'),
 path('manage/sales/',v.sales,name='sales')]
