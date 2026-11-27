from rest_framework import serializers

from .models import (Applicant, Benefit, Course, Employer, Enrollment,
                     Profession, Vacancy, VacancyMatch, WorkExperience)

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ('applicant',)

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = '__all__'
        read_only_fields = ('applicant',)

class VacancySerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.name', read_only=True)
    profession_name = serializers.CharField(source='profession.name', read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    profession_name = serializers.CharField(source='profession.name', read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = '__all__'

class ApplicantDetailSerializer(ApplicantSerializer):
    benefits = BenefitSerializer(many=True, read_only=True)
    enrollments = serializers.SerializerMethodField()
    vacancy_matches = serializers.SerializerMethodField()

    class Meta(ApplicantSerializer.Meta):
        fields = '__all__'

    def get_enrollments(self, obj):
        return [
            {
                'course': e.course.name,
                'enrolled_at': e.enrolled_at,
                'result_grade': e.result_grade,
            }
            for e in obj.enrollments.select_related('course')
        ]

    def get_vacancy_matches(self, obj):
        return [
            {
                'vacancy': m.vacancy.profession.name,
                'employer': m.vacancy.employer.name,
                'suggested_at': m.suggested_at,
                'accepted': m.accepted,
            }
            for m in obj.vacancy_matches.select_related('vacancy', 'vacancy__employer')
        ]

class EmployerSerializer(serializers.ModelSerializer):
    open_vacancies_count = serializers.SerializerMethodField()

    class Meta:
        model = Employer
        fields = '__all__'

    def get_open_vacancies_count(self, obj):
        return obj.vacancies.filter(state='open').count()

class CourseSerializer(serializers.ModelSerializer):
    profession_name = serializers.CharField(source='profession.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'

class VacancyMatchSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.__str__', read_only=True)

    class Meta:
        model = VacancyMatch
        fields = '__all__'

    def validate(self, data):
        if data['applicant'].profession_id != data['vacancy'].profession_id:
            raise serializers.ValidationError(
                'Профессия соискателя не совпадает с профессией вакансии'
            )
        return data
