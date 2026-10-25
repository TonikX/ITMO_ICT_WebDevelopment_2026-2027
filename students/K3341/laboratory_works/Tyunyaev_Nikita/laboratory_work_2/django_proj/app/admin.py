from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Discipline, Homework, HomeworkSubmission, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "class_group", "is_staff")
    list_filter = ("role", "class_group", "is_staff", "is_superuser")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "class_group", "bio")}),
        (_("Permissions"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class HomeworkSubmissionInline(admin.TabularInline):
    model = HomeworkSubmission
    extra = 0
    fields = ("student", "answer_text", "status", "grade", "is_late")
    readonly_fields = ("submitted_at",)


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "teacher", "issue_date", "due_date", "is_past_due")
    list_filter = ("subject", "teacher", "issue_date", "due_date")
    search_fields = ("title", "description")
    inlines = [HomeworkSubmissionInline]


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ("homework", "student", "status", "grade", "is_late", "submitted_at")
    list_filter = ("status", "grade", "is_late", "homework__subject")
    search_fields = ("student__username", "student__first_name", "student__last_name", "homework__title", "answer_text")
    list_editable = ("grade", "status")
    readonly_fields = ("submitted_at", "updated_at")
