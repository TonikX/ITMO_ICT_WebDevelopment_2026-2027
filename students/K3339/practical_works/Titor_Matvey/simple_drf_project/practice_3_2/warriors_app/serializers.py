from rest_framework import serializers

from .models import Profession, RaceChoices, Skill, SkillOfWarrior, Warrior

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class SkillOfWarriorSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(source='skill.title', read_only=True)

    class Meta:
        model = SkillOfWarrior
        fields = ('skill_title', 'level')

class WarriorSerializer(serializers.Serializer):

    race = serializers.ChoiceField(choices=RaceChoices.choices)
    name = serializers.CharField(max_length=120)
    level = serializers.IntegerField(min_value=0)
    profession = serializers.CharField(source='profession.title', read_only=True)
    skills = SkillOfWarriorSerializer(source='skill_ranks', many=True, read_only=True)

    def create(self, validated_data):
        return Warrior.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.race = validated_data.get('race', instance.race)
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)
        instance.save()
        return instance

class WarriorModelSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skill_ranks = SkillOfWarriorSerializer(many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = '__all__'

class WarriorDepthSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warrior
        fields = '__all__'
        depth = 1
