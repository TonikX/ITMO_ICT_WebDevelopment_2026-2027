from django.urls import path

from . import views

urlpatterns = [
    path('', views.ConferenceListView.as_view(), name='conference_list'),
    path('signup/', views.signup, name='signup'),
    path('participants/', views.ParticipantsListView.as_view(), name='participants'),
    path('conferences/new/', views.conference_create, name='conference_create'),
    path('conferences/<int:pk>/', views.conference_detail, name='conference_detail'),
    path('conferences/<int:pk>/register/', views.registration_create, name='registration_create'),
    path('conferences/<int:pk>/review/', views.review_create, name='review_create'),
    path('registrations/<int:pk>/edit/', views.registration_update, name='registration_update'),
    path('registrations/<int:pk>/delete/', views.registration_delete, name='registration_delete'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('registrations/<int:pk>/recommend/', views.registration_set_recommendation, name='registration_set_recommendation'),
]
