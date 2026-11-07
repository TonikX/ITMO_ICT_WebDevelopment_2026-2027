from django.contrib import admin
from .models import Subject, Homework, Student_answer


admin.site.register(Subject)
admin.site.register(Homework)


@admin.register(Student_answer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("student", "homework", "submitted_at", "grade")
    list_filter = ("homework__subject",)