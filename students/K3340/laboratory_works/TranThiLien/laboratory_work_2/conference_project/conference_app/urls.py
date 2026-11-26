from django.urls import path
from . import views

urlpatterns = [
    # Bài 2.1
    path('conference/<int:conference_id>/', views.conference_detail, name='conference_detail'),

    # Bài 2.2
    path('', views.conference_list, name='conference_list'),
    path('conference/create/', views.conference_create, name='conference_create'),
    path('conference/<int:conference_id>/register/',
         views.RegistrationCreateView.as_view(), name='registration_create'),
    path('registration/<int:pk>/update/',
         views.RegistrationUpdateView.as_view(), name='registration_update'),
    path('registration/<int:pk>/delete/',
         views.RegistrationDeleteView.as_view(), name='registration_delete'),
    path('conference/<int:conference_id>/review/', views.review_create, name='review_create'),

    # Bài 2.3
    path('participants/', views.participants_table, name='participants_table'),
]