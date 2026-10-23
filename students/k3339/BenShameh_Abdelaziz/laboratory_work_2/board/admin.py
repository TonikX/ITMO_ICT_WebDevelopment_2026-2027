from django.contrib import admin
from .models import Subject, Homework, Submission


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    # Columns shown in the admin's list page
    list_display = ('subject', 'teacher_name', 'date_given', 'deadline')
    list_filter = ('subject',)  # adds a filter sidebar in the admin


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'homework', 'submitted_at', 'grade')
    list_filter = ('homework__subject',)
    list_editable = ('grade',)  # lets the teacher type a grade right in the list, no need to open each row
