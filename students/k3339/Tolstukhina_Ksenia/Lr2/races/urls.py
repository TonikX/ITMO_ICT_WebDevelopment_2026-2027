from django.urls import path
from . import views

app_name = "races"

urlpatterns = [
    path("register/", views.register, name="register"),

    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("user/<int:pk>/", views.public_profile, name="public_profile"),

    path("", views.RaceListView.as_view(), name="race_list"),
    path("race/<int:pk>/", views.RaceDetailView.as_view(), name="race_detail"),
    path("race/<int:pk>/edit/", views.RaceUpdateView.as_view(), name="race_edit"),
    path("race/create/", views.RaceCreateView.as_view(), name="race_create"),
    path("race/<int:race_pk>/result/add/", views.ResultCreateView.as_view(), name="result_create"),

    path("participants/", views.participants, name="participants"),

    path("race/<int:pk>/register/", views.register_for_race, name="register_for_race"),
    path("registration/<int:pk>/delete/", views.unregister_from_race, name="unregister_from_race"),

    path("race/<int:pk>/comment/", views.add_comment, name="add_comment"),

    path("results/", views.results_table, name="results_table"),

    path("auto/create/", views.AutoCreateView.as_view(), name="auto_create"),
]

