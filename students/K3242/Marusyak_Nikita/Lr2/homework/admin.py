
from django.contrib import admin
from .models import (
    SchoolClass,
    StudentProfile,
    Subject,
    Assignment,
    Submission
)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "school_class")
    list_filter = ("school_class",)
    search_fields = ("user__username",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "school_class",
        "due_date",
        "created_by"
    )
    list_filter = ("subject", "school_class")
    search_fields = ("title", "description")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "assignment",
        "grade",
        "submitted_at"
    )
    list_filter = ("grade", "assignment")
    search_fields = (
        "student__username",
        "assignment__title"
    )
    list_editable = ("grade",)


admin.site.site_header = "Homework Board"
admin.site.site_title = "Homework Board"
admin.site.index_title = "Управление домашними заданиями"
