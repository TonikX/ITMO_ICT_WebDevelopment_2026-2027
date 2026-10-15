from django.urls import path
from . import views

urlpatterns = [
    path('conference/<int:conference_id>/', views.conference_detail, name='conference_detail'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('', views.conference_list, name='conferences'),
    path('registrations/', views.registration_report_list, name='registrations'),
    path('registration_create/<int:conference_id>/', views.registration_report_create, name='registration_create'),
    path('registration_edit/<int:registration_id>/', views.registration_report_edit, name='registration_edit'),
    path('registration_delete/<int:registration_id>/', views.registration_report_delete, name='registration_delete'),
    path('conference/<int:conference_id>/feedback/', views.feedback_create, name='feedback_create'),
    path('feedback/<int:feedback_id>/delete/', views.feedback_delete, name='feedback_delete'),
    path('conference/<int:conference_id>/participants/', views.participants_table, name='participants'),
    path('registration/<int:registration_id>/status/', views.registration_update_status, name='registration_update_status'),
]