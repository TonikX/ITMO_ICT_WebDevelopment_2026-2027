from django.urls import path

from . import views

urlpatterns = [
    path("", views.race_list, name="race_list"),
    path("register/", views.register, name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("my-entries/", views.my_entries, name="my_entries"),
    path("races/create/", views.race_create, name="race_create"),
    path("races/<int:pk>/", views.race_detail, name="race_detail"),
    path("races/<int:pk>/edit/", views.race_edit, name="race_edit"),
    path("races/<int:pk>/delete/", views.race_delete, name="race_delete"),
    path("races/<int:race_id>/enter/", views.entry_create, name="entry_create"),
    path("races/<int:race_id>/comment/", views.comment_create, name="comment_create"),
    path("races/<int:race_id>/results/add/", views.result_create, name="result_create"),
    path("entries/<int:pk>/edit/", views.entry_edit, name="entry_edit"),
    path("entries/<int:pk>/delete/", views.entry_delete, name="entry_delete"),
    path("results/<int:pk>/edit/", views.result_edit, name="result_edit"),
    path("results/<int:pk>/delete/", views.result_delete, name="result_delete"),
]
