from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Skill, Warrior
from .serializers import (
    ProfessionCreateSerializer,
    SkillOfWarriorSerializer,
    SkillSerializer,
    WarriorDetailSerializer,
    WarriorProfessionSerializer,
    WarriorSerializer,
    WarriorSkillsSerializer,
)


class WarriorAPIView(APIView):
    def get(self, request):
        warriors = Warrior.objects.all()
        serializer = WarriorSerializer(warriors, many=True)
        return Response({"Warriors": serializer.data})


class ProfessionCreateView(APIView):
    def post(self, request):
        profession = request.data.get("profession")
        serializer = ProfessionCreateSerializer(data=profession)

        if serializer.is_valid(raise_exception=True):
            profession_saved = serializer.save()

        return Response({"Success": "Profession '{}' created succesfully.".format(profession_saved.title)})


class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})

    def post(self, request):
        skill = request.data.get("skill")
        serializer = SkillSerializer(data=skill)

        if serializer.is_valid(raise_exception=True):
            skill_saved = serializer.save()

        return Response({"Success": "Skill '{}' created succesfully.".format(skill_saved.title)})


class WarriorListAPIView(generics.ListAPIView):
    queryset = Warrior.objects.all()
    serializer_class = WarriorSerializer


class WarriorProfessionsListAPIView(generics.ListAPIView):
    queryset = Warrior.objects.select_related("profession")
    serializer_class = WarriorProfessionSerializer


class WarriorSkillsListAPIView(generics.ListAPIView):
    queryset = Warrior.objects.all()
    serializer_class = WarriorSkillsSerializer


class WarriorDetailAPIView(generics.RetrieveAPIView):
    queryset = Warrior.objects.select_related("profession")
    serializer_class = WarriorDetailSerializer


class WarriorUpdateAPIView(generics.UpdateAPIView):
    queryset = Warrior.objects.all()
    serializer_class = WarriorSerializer


class WarriorDeleteAPIView(generics.DestroyAPIView):
    queryset = Warrior.objects.all()
