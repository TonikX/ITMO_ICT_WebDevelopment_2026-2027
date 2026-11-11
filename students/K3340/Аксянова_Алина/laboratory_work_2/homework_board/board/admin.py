from django.contrib import admin
from .models import Subject, Homework, Submission


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'teacher', 'assigned_date', 'due_date']
    list_filter = ['subject', 'teacher', 'due_date']
    search_fields = ['description']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'homework', 'submitted_at', 'grade']
    list_filter = ['grade', 'homework__subject']
    search_fields = ['student__username']
