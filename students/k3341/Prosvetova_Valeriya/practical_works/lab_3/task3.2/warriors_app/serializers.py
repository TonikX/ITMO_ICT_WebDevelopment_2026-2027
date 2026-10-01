from rest_framework import serializers

from .models import Profession, Skill, Warrior


class ProfessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()

    def create(self, validated_data):
        return Profession.objects.create(**validated_data)


class ProfessionSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Profession
        fields = ["title", "description"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "title"]


class SkillCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)


class WarriorSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Warrior
        fields = "__all__"


class SkillRelatedSerializer(serializers.ModelSerializer):    
    warrior_skils = WarriorSerializer(many=True)

    class Meta:
        model = Skill
        fields = ["title", "warrior_skils"]


class WarriorRelatedSerializer(serializers.ModelSerializer):        
    skill = serializers.SlugRelatedField(read_only=True, many=True, slug_field='title')
    
    
    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorDepthSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Warrior
        fields = "__all__"
        depth = 1


class WarriorNestedSerializer(serializers.ModelSerializer):  
    profession = ProfessionSerializer(read_only=True)
    skill = SkillSerializer(many=True, read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = ["id", "race", "name", "level", "profession"]


class WarriorSkillsSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(many=True, read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = ["id", "race", "name", "level", "skill"]
