from django.contrib import admin

from .models import Profession, Skill, SkillOfWarrior, Warrior


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


class SkillOfWarriorInline(admin.TabularInline):
    model = SkillOfWarrior
    extra = 1


@admin.register(Warrior)
class WarriorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "race", "level", "profession")
    inlines = [SkillOfWarriorInline]


@admin.register(SkillOfWarrior)
class SkillOfWarriorAdmin(admin.ModelAdmin):
    list_display = ("id", "warrior", "skill", "level")
