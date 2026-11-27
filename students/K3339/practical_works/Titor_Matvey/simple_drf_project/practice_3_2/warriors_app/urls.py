from django.urls import path
from rest_framework import routers

from . import views

app_name = 'warriors_app'

router = routers.DefaultRouter()
router.register('warriors_full', views.WarriorDetailAPIView, basename='warrior-full')

urlpatterns = [
    path('skills/', views.SkillAPIView.as_view(), name='skills'),
    path('warriors/', views.WarriorListAPIView.as_view(), name='warriors'),
    path('warriors_skills/', views.WarriorSkillsAPIView.as_view(), name='warriors-skills'),
    path('warriors/<int:pk>/', views.WarriorDetailAPIView.as_view(), name='warrior-detail'),
    path('warriors/<int:pk>/update/', views.WarriorUpdateAPIView.as_view(), name='warrior-update'),
    path('warriors/<int:pk>/delete/', views.WarriorDestroyAPIView.as_view(), name='warrior-delete'),
]
