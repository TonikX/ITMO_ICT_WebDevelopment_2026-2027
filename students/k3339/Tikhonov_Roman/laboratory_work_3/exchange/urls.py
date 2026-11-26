from django.urls import path

from . import views

app_name = "exchange"

urlpatterns = [
    path("professions/", views.ProfessionListCreate.as_view()),
    path("professions/<int:pk>/", views.ProfessionRetrieveUpdateDestroy.as_view()),
    path("educations/", views.EducationListCreate.as_view()),
    path("educations/<int:pk>/", views.EducationRetrieveUpdateDestroy.as_view()),
    path("employers/", views.EmployerListCreate.as_view()),
    path("employers/<int:pk>/", views.EmployerRetrieveUpdateDestroy.as_view()),
    path("courses/", views.CourseListCreate.as_view()),
    path("courses/<int:pk>/", views.CourseRetrieveUpdateDestroy.as_view()),
    path("applicants/", views.ApplicantListCreate.as_view()),
    path("applicants/<int:pk>/", views.ApplicantRetrieveUpdateDestroy.as_view()),
    path("vacancies/", views.VacancyListCreate.as_view()),
    path("vacancies/<int:pk>/", views.VacancyRetrieveUpdateDestroy.as_view()),
    path("enrollments/", views.CourseEnrollmentListCreate.as_view()),
    path("enrollments/<int:pk>/", views.CourseEnrollmentRetrieveUpdateDestroy.as_view()),
    path("applications/", views.ApplicationListCreate.as_view()),
    path("applications/<int:pk>/", views.ApplicationRetrieveUpdateDestroy.as_view()),
    path("allowances/", views.AllowanceListCreate.as_view()),
    path("allowances/<int:pk>/", views.AllowanceRetrieveUpdateDestroy.as_view()),
    path("analytics/professions-without-vacancies/", views.ProfessionsWithoutVacanciesView.as_view()),
    path("analytics/matching-vacancies/", views.MatchingVacanciesView.as_view()),
    path("analytics/offer-days/", views.OfferDaysView.as_view()),
    path("analytics/active-allowances/", views.ActiveAllowancesView.as_view()),
    path("analytics/high-education-vacancies/", views.HighEducationVacanciesView.as_view()),
    path("reports/employers-open-vacancies/", views.EmployerOpenVacanciesReportView.as_view()),
]
