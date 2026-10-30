from django.contrib import admin

from .models import Profession, Skill, SkillOfWarrior, Warrior

admin.site.register([Profession, Skill, Warrior, SkillOfWarrior])
