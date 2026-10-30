from django.urls import path

from . import views

app_name = "warriors_app"
urlpatterns = [
    path("skills/", views.SkillListAPIView.as_view(), name="skill-list"),
    path("skills/create/", views.SkillCreateAPIView.as_view(), name="skill-create"),
    path("warriors/professions/", views.WarriorProfessionListAPIView.as_view(), name="warrior-professions"),
    path("warriors/skills/", views.WarriorSkillsListAPIView.as_view(), name="warrior-skills"),
    path("warriors/<int:pk>/", views.WarriorRetrieveAPIView.as_view(), name="warrior-detail"),
    path("warriors/<int:pk>/delete/", views.WarriorDestroyAPIView.as_view(), name="warrior-delete"),
    path("warriors/<int:pk>/update/", views.WarriorUpdateAPIView.as_view(), name="warrior-update"),
]
