from django.contrib import admin

from .models import (Applicant, Benefit, Course, Employer, Enrollment,
                     Profession, Vacancy, VacancyMatch, WorkExperience)

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'profession', 'education', 'grade',
                    'experience_years', 'last_salary', 'registered_at')
    list_filter = ('education', 'profession')
    search_fields = ('full_name', 'passport')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'company', 'position', 'started_at', 'ended_at')
    list_filter = ('company',)

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'contact_person', 'phone')
    search_fields = ('name',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('profession', 'employer', 'salary', 'posted_at', 'state')
    list_filter = ('state', 'profession', 'employer')
    search_fields = ('extra_info',)

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'amount', 'started_at', 'ended_at')
    list_filter = ('started_at',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'profession', 'started_at', 'ended_at')
    list_filter = ('profession',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'course', 'enrolled_at', 'result_grade')
    list_filter = ('course',)

@admin.register(VacancyMatch)
class VacancyMatchAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'vacancy', 'suggested_at', 'accepted')
    list_filter = ('accepted',)
