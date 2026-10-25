from django.urls import path

from . import views

urlpatterns = [
    # Список заданий и главная
    path("", views.HomeworkListView.as_view(), name="homework_list"),
    path("homeworks/", views.HomeworkListView.as_view(), name="homework_list_alias"),
    # Просмотр, создание, редактирование и удаление ДЗ
    path("homeworks/create/", views.HomeworkCreateView.as_view(), name="homework_create"),
    path("homeworks/<int:pk>/", views.HomeworkDetailView.as_view(), name="homework_detail"),
    path("homeworks/<int:pk>/edit/", views.HomeworkUpdateView.as_view(), name="homework_update"),
    path("homeworks/<int:pk>/delete/", views.HomeworkDeleteView.as_view(), name="homework_delete"),
    # Сдача работы учеником
    path("homeworks/<int:pk>/submit/", views.submit_homework, name="homework_submit"),
    # Выставление оценки преподавателем
    path("submissions/<int:pk>/grade/", views.grade_submission, name="submission_grade"),
    # Классный журнал (сводная таблица оценок)
    path("gradebook/", views.GradebookView.as_view(), name="gradebook"),
    # Аутентификация и профиль
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
