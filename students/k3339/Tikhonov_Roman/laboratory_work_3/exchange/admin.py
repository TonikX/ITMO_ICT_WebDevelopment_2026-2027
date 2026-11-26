from django.contrib import admin

from .models import (
    Allowance,
    Applicant,
    Application,
    Course,
    CourseEnrollment,
    Education,
    Employer,
    Profession,
    Vacancy,
)

admin.site.register(
    [
        Profession,
        Education,
        Employer,
        Course,
        Applicant,
        Vacancy,
        CourseEnrollment,
        Application,
        Allowance,
    ]
)
