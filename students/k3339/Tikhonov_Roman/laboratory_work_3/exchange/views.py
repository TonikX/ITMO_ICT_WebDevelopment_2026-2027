from django.db.models import DurationField, ExpressionWrapper, F, Prefetch
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

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
from .serializers import (
    AllowanceSerializer,
    ApplicantDetailSerializer,
    ApplicantSerializer,
    ApplicationSerializer,
    CourseApplicantsSerializer,
    CourseEnrollmentSerializer,
    CourseSerializer,
    EducationSerializer,
    EmployerDetailSerializer,
    EmployerSerializer,
    ProfessionSerializer,
    VacancySerializer,
)


class ProfessionListCreate(generics.ListCreateAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class ProfessionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class EducationListCreate(generics.ListCreateAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class EducationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class EmployerListCreate(generics.ListCreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer


class EmployerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employer.objects.select_related().prefetch_related("vacancies")
    serializer_class = EmployerDetailSerializer


class CourseListCreate(generics.ListCreateAPIView):
    queryset = Course.objects.select_related("profession")
    serializer_class = CourseSerializer


class CourseRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.select_related("profession").prefetch_related("enrollments__applicant")
    serializer_class = CourseApplicantsSerializer


class ApplicantListCreate(generics.ListCreateAPIView):
    queryset = Applicant.objects.select_related("profession", "education")
    serializer_class = ApplicantSerializer


class ApplicantRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Applicant.objects.select_related("profession", "education").prefetch_related(
        "applications__vacancy", "allowances", "enrollments__course"
    )
    serializer_class = ApplicantDetailSerializer


class VacancyListCreate(generics.ListCreateAPIView):
    queryset = Vacancy.objects.select_related("employer", "profession", "education")
    serializer_class = VacancySerializer


class VacancyRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.select_related("employer", "profession", "education")
    serializer_class = VacancySerializer


class CourseEnrollmentListCreate(generics.ListCreateAPIView):
    queryset = CourseEnrollment.objects.select_related("applicant", "course")
    serializer_class = CourseEnrollmentSerializer


class CourseEnrollmentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseEnrollment.objects.select_related("applicant", "course")
    serializer_class = CourseEnrollmentSerializer


class ApplicationListCreate(generics.ListCreateAPIView):
    queryset = Application.objects.select_related("applicant", "vacancy")
    serializer_class = ApplicationSerializer


class ApplicationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.select_related("applicant", "vacancy")
    serializer_class = ApplicationSerializer


class AllowanceListCreate(generics.ListCreateAPIView):
    queryset = Allowance.objects.select_related("applicant")
    serializer_class = AllowanceSerializer


class AllowanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Allowance.objects.select_related("applicant")
    serializer_class = AllowanceSerializer


class ProfessionsWithoutVacanciesView(APIView):
    def get(self, request):
        professions = (
            Profession.objects.filter(applicants__isnull=False)
            .exclude(id__in=Vacancy.objects.values("profession_id"))
            .distinct()
        )
        serializer = ProfessionSerializer(professions, many=True)
        return Response(serializer.data)


class MatchingVacanciesView(APIView):
    def get(self, request):
        result = []
        for applicant in Applicant.objects.select_related("profession", "education"):
            vacancies = Vacancy.objects.filter(
                status=Vacancy.Status.OPEN,
                profession_id=applicant.profession_id,
                education__priority__lte=applicant.education.priority,
                required_experience__lte=applicant.experience_years,
                required_rank__lte=applicant.rank,
            ).select_related("employer", "profession", "education")
            result.append({
                "applicant": ApplicantSerializer(applicant).data,
                "matching_vacancies": VacancySerializer(vacancies, many=True).data,
            })
        return Response(result)


class OfferDaysView(APIView):
    def get(self, request):
        applications = (
            Application.objects.filter(
                vacancy__status=Vacancy.Status.OPEN,
                offer_date__isnull=False,
            )
            .select_related("applicant", "vacancy")
            .annotate(
                days_since_offer=ExpressionWrapper(
                    timezone.localdate() - F("offer_date"),
                    output_field=DurationField(),
                )
            )
        )
        result = [
            {
                "applicant": str(application.applicant),
                "vacancy": str(application.vacancy),
                "offer_date": application.offer_date,
                "days_since_offer": application.days_since_offer.days,
            }
            for application in applications
        ]
        return Response(result)


class ActiveAllowancesView(APIView):
    def get(self, request):
        count = Allowance.objects.filter(status=Allowance.Status.ACTIVE).count()
        return Response({"active_allowances": count})


class HighEducationVacanciesView(APIView):
    def get(self, request):
        count = Vacancy.objects.filter(
            education__level__iexact="высшее",
            salary_min__gte=5000,
            salary_max__lte=60000,
        ).count()
        return Response({"vacancies_count": count})


class EmployerOpenVacanciesReportView(APIView):
    def get(self, request):
        employers = Employer.objects.prefetch_related(
            Prefetch(
                "vacancies",
                queryset=Vacancy.objects.filter(status=Vacancy.Status.OPEN),
            )
        )
        result = []
        for employer in employers:
            vacancies = employer.vacancies.all()
            result.append({
                "employer": EmployerSerializer(employer).data,
                "open_vacancies": VacancySerializer(vacancies, many=True).data,
                "open_vacancies_count": vacancies.count(),
            })
        return Response(result)
