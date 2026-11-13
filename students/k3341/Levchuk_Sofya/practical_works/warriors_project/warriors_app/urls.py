from django.urls import path
from .views import *

app_name = "warriors_app"

urlpatterns = [
    path('warriors/', WarriorAPIView.as_view()),
    path('profession/create/', ProfessionCreateView.as_view()),

    path('skills/', SkillAPIView.as_view()),
    path('skills/create/', SkillCreateView.as_view()),

    path('warriors/list/', WarriorListAPIView.as_view()),
    path('profession/generic_create/', ProfessionCreateAPIView.as_view()),

    path('warriors/with-professions/', WarriorsProfessionsView.as_view()),
    path('warriors/with-skills/', WarriorsSkillsView.as_view()),
    path('warriors/<int:pk>/', WarriorDetailView.as_view()),
    path('warriors/<int:pk>/delete/', WarriorDeleteView.as_view()),
    path('warriors/<int:pk>/update/', WarriorUpdateView.as_view()),
]