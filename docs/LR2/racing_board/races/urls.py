from django.urls import path

from .views import (
    RaceListView,
    register,
    user_login,
    user_logout,
    profile,
    register_for_race,
    my_registrations,
    manage_registrations,
    update_registration_status,
    race_detail,
)


urlpatterns = [
    path('', RaceListView.as_view(), name='race_list'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),

    path(
        'my-registrations/',
        my_registrations,
        name='my_registrations',
    ),

    path(
        'manage-registrations/',
        manage_registrations,
        name='manage_registrations',
    ),

    path(
        'manage-registrations/<int:registration_id>/status/',
        update_registration_status,
        name='update_registration_status',
    ),

    path(
        '<int:race_id>/register/',
        register_for_race,
        name='register_for_race',
    ),

    path(
        '<int:race_id>/',
        race_detail,
        name='race_detail',
    ),
]