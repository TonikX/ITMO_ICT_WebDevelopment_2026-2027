from django.contrib import admin

from .models import Homework, Subject, Submission


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("subject", "teacher", "issued", "due")
    list_filter = ("subject",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("homework", "student", "grade", "submitted_at")
    list_filter = ("homework__subject", "grade")
    search_fields = ("student__last_name", "student__first_name")


admin.site.register(Subject)
