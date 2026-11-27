from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('professions', views.ProfessionViewSet)
router.register('applicants', views.ApplicantViewSet)
router.register('work-experiences', views.WorkExperienceViewSet)
router.register('employers', views.EmployerViewSet)
router.register('vacancies', views.VacancyViewSet)
router.register('benefits', views.BenefitViewSet)
router.register('courses', views.CourseViewSet)
router.register('enrollments', views.EnrollmentViewSet)
router.register('vacancy-matches', views.VacancyMatchViewSet)

urlpatterns = router.urls
