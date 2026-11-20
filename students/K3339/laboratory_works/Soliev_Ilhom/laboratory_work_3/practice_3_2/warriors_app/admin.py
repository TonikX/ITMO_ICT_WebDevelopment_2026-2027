from django.contrib import admin

from .models import Profession, Skill, SkillOfWarrior, Warrior


class SkillOfWarriorInline(admin.TabularInline):
    model = SkillOfWarrior
    extra = 0


@admin.register(Warrior)
class WarriorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "race", "level", "profession")
    list_filter = ("race", "profession")
    search_fields = ("name",)
    inlines = (SkillOfWarriorInline,)


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    search_fields = ("title",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("title",)
