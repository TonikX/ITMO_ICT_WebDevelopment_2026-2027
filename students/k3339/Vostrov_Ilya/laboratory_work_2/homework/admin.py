"""Панель администратора"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Homework, Profile, Submission


class ProfileInline(admin.StackedInline):
    """Поле "Класс / учебная группа" прямо в админке пользователя."""

    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


# Переопределяем стандартный UserAdmin, чтобы была видна учебная группа.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'issue_date', 'deadline')
    list_filter = ('subject', 'teacher')
    list_editable = ('teacher',)
    search_fields = ('subject', 'teacher', 'text')
    date_hierarchy = 'deadline'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'short_text', 'submitted_at', 'mark', 'marked_at')
    list_filter = ('homework__subject', 'mark')
    search_fields = ('student__username', 'student__profile__group', 'text', 'homework__subject')
    list_select_related = ('homework', 'student')

    @admin.display(description='Текст решения')
    def short_text(self, obj):
        return (obj.text[:50] + '…') if len(obj.text) > 50 else obj.text

    def save_model(self, request, obj, form, change):
        """Автоматически проставляем дату выставления отметки."""
        if obj.mark is not None and not obj.marked_at:
            obj.marked_at = timezone.now()
        super().save_model(request, obj, form, change)
