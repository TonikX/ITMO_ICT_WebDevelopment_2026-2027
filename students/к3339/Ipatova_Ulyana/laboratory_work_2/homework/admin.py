from django.contrib import admin

from .forms import HomeworkForm
from .models import Homework, StudentProfile, StudyGroup, Subject, Submission


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name',)
    search_fields = ('group_name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name',)
    search_fields = ('subject_name',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'study_group')
    list_filter = ('study_group',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    form = HomeworkForm
    fields = ('subject', 'study_group', 'teacher', 'issue_at', 'deadline', 'description', 'penalty_info')
    list_display = ('subject', 'study_group', 'teacher', 'issue_at', 'deadline')
    list_filter = ('subject', 'study_group', 'teacher')
    search_fields = ('description', 'subject__subject_name', 'teacher__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('subject', 'study_group', 'teacher')
        if not request.user.is_superuser:
            queryset = queryset.filter(teacher=request.user)
        return queryset

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj is not None and request.method == 'POST':
            obj = self.get_queryset(request).select_for_update().get(pk=obj.pk)
        return obj

    def has_view_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser and obj.teacher_id != request.user.pk:
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser and obj.teacher_id != request.user.pk:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser and obj.teacher_id != request.user.pk:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if not request.user.is_superuser:
            fields.append('teacher')
        if obj is not None and obj.submissions.exists():
            fields.extend(HomeworkForm.fixed_fields)
        return fields

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.teacher = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            teachers = db_field.remote_field.model.objects.filter(is_staff=True)
            if not request.user.is_superuser:
                teachers = teachers.filter(pk=request.user.pk)
            kwargs['queryset'] = teachers
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'homework', 'submitted_at', 'grade')
    list_filter = ('homework__study_group', 'homework__subject', 'grade')
    search_fields = ('student__username', 'student__last_name', 'answer_text')
    readonly_fields = ('submitted_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related(
            'student', 'homework__subject', 'homework__study_group', 'homework__teacher'
        )
        if not request.user.is_superuser:
            queryset = queryset.filter(homework__teacher=request.user)
        return queryset

    def has_view_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser and obj.homework.teacher_id != request.user.pk:
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser and obj.homework.teacher_id != request.user.pk:
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return ('student', 'homework', 'answer_text', 'submitted_at')

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
        else:
            obj.save(update_fields=['grade'])
