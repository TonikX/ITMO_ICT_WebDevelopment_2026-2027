from django.urls import path

from . import views

urlpatterns = [
    path("", views.conference_list, name="conference_list"),
    path("conferences/<int:pk>/", views.conference_detail, name="conference_detail"),
    path("signup/", views.sign_up, name="signup"),
    path("my-registrations/", views.my_registrations, name="my_registrations"),
    path("conferences/<int:pk>/register/", views.registration_create, name="registration_create"),
    path("registrations/<int:pk>/edit/", views.registration_edit, name="registration_edit"),
    path("registrations/<int:pk>/delete/", views.registration_delete, name="registration_delete"),
    path("conferences/<int:pk>/review/", views.review_edit, name="review_edit"),
    path("participants/", views.participants, name="participants"),
    path("organizer/", views.staff_registrations, name="staff_registrations"),
    path("organizer/<int:pk>/result/", views.result_edit, name="result_edit"),
]
