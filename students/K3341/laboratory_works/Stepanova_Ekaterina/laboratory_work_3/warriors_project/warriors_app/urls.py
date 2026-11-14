from django.urls import path
from .views import *

app_name = "warriors_app"

urlpatterns = [
    path('warriors/', WarriorAPIView.as_view()),
    path('profession/create/', ProfessionCreateView.as_view()),
    path('skill/create/', SkillCreateView.as_view()),
    path('skills/', SkillAPIView.as_view()),
    path('warriors/professions/', WarriorProfessionListView.as_view()),
    path('warriors/skills/', WarriorSkillListView.as_view()),
    path('warriors/profession_skills/', WarriorSkillProfessionListView.as_view()),
    path('warriors/delete/<int:pk>/', WarriorDeleteView.as_view()),
    path('warriors/update/<int:pk>/', WarriorUpdateView.as_view()),

]