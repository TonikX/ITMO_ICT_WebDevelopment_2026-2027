from rest_framework import generics, views
from rest_framework.response import Response

from .models import Skill, Warrior
from .serializers import (SkillSerializer, WarriorModelSerializer,
                          WarriorSerializer)

class SkillAPIView(views.APIView):

    def get(self, request):
        skills = Skill.objects.all()
        return Response(SkillSerializer(skills, many=True).data)

    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class WarriorListAPIView(generics.ListAPIView):

    queryset = Warrior.objects.select_related('profession').all()
    serializer_class = WarriorModelSerializer

class WarriorSkillsAPIView(views.APIView):

    def get(self, request):
        warriors = Warrior.objects.select_related('profession').prefetch_related('skill_ranks__skill')
        data = [
            {
                'id': w.id,
                'name': w.name,
                'race': w.get_race_display(),
                'level': w.level,
                'profession': w.profession.title if w.profession else None,
                'skills': [
                    {'title': sr.skill.title, 'level': sr.level}
                    for sr in w.skill_ranks.all()
                ],
            }
            for w in warriors
        ]
        return Response(data)

class WarriorDetailAPIView(generics.RetrieveAPIView):

    queryset = Warrior.objects.select_related('profession').prefetch_related('skill_ranks__skill')
    serializer_class = WarriorModelSerializer

class WarriorUpdateAPIView(generics.UpdateAPIView):

    queryset = Warrior.objects.all()
    serializer_class = WarriorSerializer

class WarriorDestroyAPIView(generics.DestroyAPIView):

    queryset = Warrior.objects.all()
