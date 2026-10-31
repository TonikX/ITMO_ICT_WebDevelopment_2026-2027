"""Адреса каталога и действий с конференциями."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.conference_list, name="conference_list"),
    path("conferences/<int:pk>/", views.conference_detail, name="conference_detail"),
    path(
        "conferences/<int:pk>/register/",
        views.registration_create,
        name="registration_create",
    ),
    path(
        "registrations/<int:pk>/edit/",
        views.registration_edit,
        name="registration_edit",
    ),
    path(
        "registrations/<int:pk>/delete/",
        views.registration_delete,
        name="registration_delete",
    ),
    path("conferences/<int:pk>/review/", views.review_create, name="review_create"),
    path("participants/", views.participants, name="participants"),
    path("registrations/<int:pk>/result/", views.result_edit, name="result_edit"),
]
