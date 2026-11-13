from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *


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

        return Response({"Success": "Profession '{}' created successfully.".format(profession_saved.title)})


class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})


class SkillCreateView(APIView):
    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            skill_saved = serializer.save()
        return Response({"Success": "Скилл '{}' создан".format(skill_saved.title)})


class WarriorListAPIView(generics.ListAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class ProfessionCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfessionCreateSerializer
    queryset = Profession.objects.all()

class WarriorsProfessionsView(generics.ListAPIView):
    serializer_class = WarriorProfessionSerializer
    queryset = Warrior.objects.all()


class WarriorsSkillsView(generics.ListAPIView):
    serializer_class = WarriorSkillsSerializer
    queryset = Warrior.objects.all()


class WarriorDetailView(generics.RetrieveAPIView):
    serializer_class = WarriorNestedSerializer
    queryset = Warrior.objects.all()


class WarriorDeleteView(generics.DestroyAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class WarriorUpdateView(generics.UpdateAPIView):
    serializer_class = WarriorUpdateSerializer
    queryset = Warrior.objects.all()