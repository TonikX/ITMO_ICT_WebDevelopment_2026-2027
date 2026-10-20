from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profession, Skill, Warrior
from .serializers import (
    ProfessionCreateSerializer,
    SkillCreateSerializer,
    SkillRelatedSerializer,
    SkillSerializer,
    WarriorDepthSerializer,
    WarriorNestedSerializer,
    WarriorProfessionSerializer,
    WarriorRelatedSerializer,
    WarriorSerializer,
    WarriorSkillsSerializer,
)


# --- APIView ---      

class WarriorAPIView(APIView):
    def get(self, request):
        warriors = Warrior.objects.all()
        serializer = WarriorSerializer(warriors, many=True)
        return Response({"Warriors": serializer.data})


class ProfessionCreateView(APIView):
    def post(self, request):
        profession = request.data.get("profession")
        serializer = ProfessionCreateSerializer(data=profession)
        serializer.is_valid(raise_exception=True)
        profession_saved = serializer.save()
        return Response({"Success": "Profession '{}' created succesfully.".format(profession_saved.title)})


# --- Практическое задание 1: умения через APIView ---

class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})


class SkillCreateView(APIView):
    def post(self, request):
        skill = request.data.get("skill")
        serializer = SkillCreateSerializer(data=skill)
        serializer.is_valid(raise_exception=True)
        skill_saved = serializer.save()
        return Response({"Success": "Skill '{}' created succesfully.".format(skill_saved.title)})


# --- Generic views --- 

class WarriorListAPIView(generics.ListAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class ProfessionCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfessionCreateSerializer
    queryset = Profession.objects.all()


class WarriorCreateAPIView(generics.CreateAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()
   

    def perform_create(self, serializer):
        serializer.save()


# --- Демонстрация сериализаторов ---  

class WarriorRelatedListAPIView(generics.ListAPIView):
    serializer_class = WarriorRelatedSerializer
    queryset = Warrior.objects.all()


class WarriorDepthListAPIView(generics.ListAPIView):
    serializer_class = WarriorDepthSerializer
    queryset = Warrior.objects.all()


class SkillRelatedListAPIView(generics.ListAPIView):
    serializer_class = SkillRelatedSerializer
    queryset = Skill.objects.all()


# --- Практическое задание 2: CRUD воинов ---

class WarriorProfessionListAPIView(generics.ListAPIView):
    serializer_class = WarriorProfessionSerializer
    queryset = Warrior.objects.select_related('profession')


class WarriorSkillsListAPIView(generics.ListAPIView):
    serializer_class = WarriorSkillsSerializer
    queryset = Warrior.objects.prefetch_related('skill')


class WarriorRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = WarriorNestedSerializer
    queryset = Warrior.objects.select_related('profession').prefetch_related('skill')


class WarriorDestroyAPIView(generics.DestroyAPIView):
    queryset = Warrior.objects.all()


class WarriorUpdateAPIView(generics.UpdateAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()
