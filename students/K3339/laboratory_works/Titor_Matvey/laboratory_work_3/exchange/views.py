from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (Applicant, Benefit, Course, Employer, Enrollment,
                     Profession, Vacancy, VacancyMatch, WorkExperience)
from .serializers import (ApplicantDetailSerializer, ApplicantSerializer,
                          BenefitSerializer, CourseSerializer,
                          EmployerSerializer, EnrollmentSerializer,
                          ProfessionSerializer, VacancyMatchSerializer,
                          VacancySerializer, WorkExperienceSerializer)

EDUCATION_ORDER = {'primary': 1, 'secondary': 2, 'vocational': 3, 'higher': 4}

class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

    @action(detail=False, methods=['get'], url_path='unrepresented')
    def unrepresented(self, request):
        professions = Profession.objects.filter(vacancies__isnull=True)
        serializer = self.get_serializer(professions, many=True)
        return Response(serializer.data)

class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.select_related('profession').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApplicantDetailSerializer
        return ApplicantSerializer

    @action(detail=True, methods=['get'], url_path='matching_vacancies')
    def matching_vacancies(self, request, pk=None):
        try:
            applicant = Applicant.objects.get(pk=pk)
        except Applicant.DoesNotExist:
            return Response({'detail': 'Соискатель не найден'}, status=status.HTTP_404_NOT_FOUND)

        allowed_education = [
            code for code, rank in EDUCATION_ORDER.items()
            if rank >= EDUCATION_ORDER[applicant.education]
        ]
        vacancies = Vacancy.objects.filter(
            state='open',
            profession_id=applicant.profession_id,
            education__in=allowed_education,
        )
        if applicant.grade is not None:
            vacancies = vacancies.filter(
                Q(grade__isnull=True) | Q(grade__lte=applicant.grade)
            )
        vacancies = vacancies.exclude(min_experience__gt=applicant.experience_years)

        serializer = VacancySerializer(vacancies, many=True)
        return Response(serializer.data)

class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.select_related('applicant').all()
    serializer_class = WorkExperienceSerializer

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.prefetch_related('vacancies').all()
    serializer_class = EmployerSerializer

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.select_related('employer', 'profession').all()
    serializer_class = VacancySerializer

    @action(detail=False, methods=['get'], url_path='unclosed_days')
    def unclosed_days(self, request):
        today = timezone.localdate()
        vacancies = Vacancy.objects.exclude(state='closed')
        result = [
            {
                'id': v.id,
                'profession': v.profession.name,
                'employer': v.employer.name,
                'posted_at': v.posted_at,
                'days_open': (today - v.posted_at).days,
                'state': v.state,
            }
            for v in vacancies.select_related('profession', 'employer')
        ]
        result.sort(key=lambda item: item['days_open'], reverse=True)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='premium')
    def premium(self, request):
        vacancies = Vacancy.objects.filter(
            education='higher',
            salary__gte=5000,
            salary__lte=60000,
        )
        serializer = self.get_serializer(vacancies, many=True)
        return Response(serializer.data)

class BenefitViewSet(viewsets.ModelViewSet):
    queryset = Benefit.objects.select_related('applicant').all()
    serializer_class = BenefitSerializer

    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        today = timezone.localdate()
        benefits = Benefit.objects.filter(
            started_at__lte=today,
        ).filter(Q(ended_at__isnull=True) | Q(ended_at__gte=today))
        serializer = self.get_serializer(benefits, many=True)
        return Response(serializer.data)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('profession').all()
    serializer_class = CourseSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('applicant', 'course').all()
    serializer_class = EnrollmentSerializer

class VacancyMatchViewSet(viewsets.ModelViewSet):
    queryset = VacancyMatch.objects.select_related('applicant', 'vacancy').all()
    serializer_class = VacancyMatchSerializer
