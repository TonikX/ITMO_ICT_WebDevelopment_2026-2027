from rest_framework import serializers

from .models import Profession, Skill, SkillOfWarrior, Warrior


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = "__all__"


class ProfessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()

    def create(self, validated_data):
        profession = Profession(**validated_data)
        profession.save()
        return profession


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class SkillOfWarriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillOfWarrior
        fields = "__all__"


class WarriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer()

    class Meta:
        model = Warrior
        fields = ["id", "name", "race", "level", "profession"]


class WarriorSkillsSerializer(serializers.ModelSerializer):
    warrior_skill = SkillOfWarriorSerializer(many=True)

    class Meta:
        model = Warrior
        fields = ["id", "name", "race", "level", "warrior_skill"]


class WarriorDetailSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer()
    warrior_skill = SkillOfWarriorSerializer(many=True)

    class Meta:
        model = Warrior
        fields = ["id", "name", "race", "level", "profession", "warrior_skill"]
