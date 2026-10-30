from rest_framework import serializers

from .models import Profession, Skill, SkillOfWarrior, Warrior


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "title")


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ("id", "title", "description")


class SkillOfWarriorSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillOfWarrior
        fields = ("id", "skill", "level")


class WarriorProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "race", "name", "level", "profession")


class WarriorSkillsSerializer(serializers.ModelSerializer):
    skill = SkillOfWarriorSerializer(source="warrior_skills", many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "race", "name", "level", "skill")


class WarriorDetailSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skill = SkillOfWarriorSerializer(source="warrior_skills", many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "race", "name", "level", "profession", "skill")


class WarriorUpdateSerializer(serializers.ModelSerializer):
    # Профессия передаётся по ID; навыки читаются через промежуточную модель.
    class Meta:
        model = Warrior
        fields = ("id", "race", "name", "level", "profession")
