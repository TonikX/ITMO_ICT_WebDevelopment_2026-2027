from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models import StudentProfile, Task, Work


class GroupInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Карточка ученика'


class UserWithGroup(UserAdmin):
    inlines = (GroupInline,)


admin.site.unregister(User)
admin.site.register(User, UserWithGroup)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('discipline', 'teacher_name', 'issued_on', 'due_on', 'id')
    list_filter = ('discipline',)
    search_fields = ('discipline', 'teacher_name', 'body')
    date_hierarchy = 'due_on'


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'cut_body', 'sent_at', 'score', 'scored_at')
    list_filter = ('task__discipline', 'score')
    search_fields = ('student__username', 'student__card__study_group', 'body')
    list_select_related = ('task', 'student')

    @admin.display(description='Решение')
    def cut_body(self, obj):
        return obj.body[:60] + '…' if len(obj.body) > 60 else obj.body

    def save_model(self, request, obj, form, change):
        if obj.score is not None and obj.scored_at is None:
            obj.scored_at = timezone.now()
        super().save_model(request, obj, form, change)
