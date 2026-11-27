from datetime import date, timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from exchange.models import (Applicant, Benefit, Course, Employer, Enrollment,
                             Profession, Vacancy, VacancyMatch, WorkExperience)

TODAY = date.today()

def auth(case):
    User.objects.create_user('writer', password='pass12345')
    r = case.client.post('/api/v1/token/login/', {
        'username': 'writer', 'password': 'pass12345',
    }, format='json')
    case.client.credentials(HTTP_AUTHORIZATION='Token ' + r.data['auth_token'])

def base_data():
    prof_cook = Profession.objects.create(name='Повар')
    prof_dev = Profession.objects.create(name='Программист')
    prof_welder = Profession.objects.create(name='Сварщик')
    emp1 = Employer.objects.create(
        name='ООО «Еда»', address='СПб, Невский пр., 1',
        contact_person='Ирина Иванова', phone='+7 812 111-11-11',
    )
    emp2 = Employer.objects.create(
        name='ООО «Металл»', address='СПб, Обводный канал, 5',
        contact_person='Пётр Петров', phone='+7 812 222-22-22',
    )
    v_cook = Vacancy.objects.create(
        employer=emp1, profession=prof_cook, education='secondary',
        min_experience=1, grade=2, salary=50000, posted_at=TODAY - timedelta(days=10),
        state='open',
    )
    v_closed = Vacancy.objects.create(
        employer=emp1, profession=prof_cook, education='primary',
        min_experience=0, salary=30000, posted_at=TODAY - timedelta(days=60),
        state='closed',
    )
    v_dev = Vacancy.objects.create(
        employer=emp2, profession=prof_dev, education='higher',
        min_experience=3, grade=4, salary=58000, posted_at=TODAY - timedelta(days=20),
        state='open',
    )
    a_cook = Applicant.objects.create(
        full_name='Анна Соколова', birth_date=date(2001, 9, 3), passport='7800 111111',
        education='secondary', profession=prof_cook, grade=2,
        experience_years=1, last_salary=35000, registered_at=TODAY - timedelta(days=30),
    )
    a_dev = Applicant.objects.create(
        full_name='Олег Кузнецов', birth_date=date(1998, 4, 12), passport='7800 222222',
        education='higher', profession=prof_dev, grade=3,
        experience_years=4, last_salary=52000, registered_at=TODAY - timedelta(days=40),
    )
    return prof_cook, prof_dev, prof_welder, emp1, emp2, v_cook, v_closed, v_dev, a_cook, a_dev

class AuthTests(APITestCase):
    def test_register_login_me(self):
        r = self.client.post('/api/v1/users/', {
            'username': 'newuser', 'password': 'strong-pass-777',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.client.post('/api/v1/token/login/', {
            'username': 'newuser', 'password': 'strong-pass-777',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        token = r.data['auth_token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        r = self.client.get('/api/v1/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'newuser')

    def test_logout_invalidates_token(self):
        User.objects.create_user('u1', password='pass12345')
        r = self.client.post('/api/v1/token/login/', {
            'username': 'u1', 'password': 'pass12345',
        }, format='json')
        token = r.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(self.client.post('/api/v1/token/logout/').status_code,
                         status.HTTP_204_NO_CONTENT)
        r = self.client.get('/api/v1/users/me/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

class WritePermissionTests(APITestCase):
    def test_read_public_write_needs_auth(self):
        Profession.objects.create(name='Повар')
        r = self.client.get('/api/v1/professions/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.client.post('/api/v1/professions/', {'name': 'Сварщик'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

        User.objects.create_user('u1', password='pass12345')
        r = self.client.post('/api/v1/token/login/', {
            'username': 'u1', 'password': 'pass12345',
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + r.data['auth_token'])
        r = self.client.post('/api/v1/professions/', {'name': 'Сварщик'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

class ApplicantTests(APITestCase):
    def test_detail_includes_nested(self):
        (prof_cook, prof_dev, _pw, _e1, _e2, _vc, _vd, _vp, a_cook, _ad) = base_data()
        WorkExperience.objects.create(
            applicant=a_cook, company='Кафе «Балкон»', position='Повар',
            started_at=date(2023, 2, 1),
        )
        Benefit.objects.create(
            applicant=a_cook, amount=9900,
            started_at=TODAY - timedelta(days=10),
            ended_at=TODAY + timedelta(days=80),
        )
        r = self.client.get(f'/api/v1/applicants/{a_cook.pk}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['work_experiences']), 1)
        self.assertEqual(len(r.data['benefits']), 1)

    def test_create_and_delete_applicant(self):
        auth(self)
        prof = Profession.objects.create(name='Повар')
        payload = {
            'full_name': 'Тест Тестович', 'birth_date': '2000-01-01',
            'passport': '7800 999999', 'education': 'higher',
            'profession': prof.pk, 'experience_years': 2,
            'registered_at': '2026-01-01',
        }
        r = self.client.post('/api/v1/applicants/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        pk = r.data['id']
        r = self.client.delete(f'/api/v1/applicants/{pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Applicant.objects.filter(pk=pk).exists())

class MatchingTests(APITestCase):
    def setUp(self):
        (_, _, _, _, _, v_cook, v_closed, v_dev, a_cook, a_dev) = base_data()
        self.v_cook, self.v_closed, self.v_dev = v_cook, v_closed, v_dev
        self.a_cook, self.a_dev = a_cook, a_dev

    def test_match_by_profession_and_grade(self):
        r = self.client.get(f'/api/v1/applicants/{self.a_cook.pk}/matching_vacancies/')
        ids = [v['id'] for v in r.data]
        self.assertIn(self.v_cook.id, ids)
        self.assertNotIn(self.v_dev.id, ids)
        self.assertNotIn(self.v_closed.id, ids)

    def test_no_match_wrong_education(self):
        self.a_dev.education = 'primary'
        self.a_dev.save()
        r = self.client.get(f'/api/v1/applicants/{self.a_dev.pk}/matching_vacancies/')
        ids = [v['id'] for v in r.data]
        self.assertNotIn(self.v_dev.id, ids)

    def test_404_for_missing_applicant(self):
        r = self.client.get('/api/v1/applicants/999/matching_vacancies/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

class QueryEndpointTests(APITestCase):
    def setUp(self):
        (prof_cook, prof_dev, prof_welder, emp1, emp2,
         v_cook, v_closed, v_dev, a_cook, a_dev) = base_data()
        self.prof_dev = prof_dev
        self.v_dev = v_dev
        self.a_dev = a_dev

    def test_active_benefits(self):
        active = Benefit.objects.create(
            applicant=self.a_dev, amount=10000,
            started_at=TODAY - timedelta(days=5),
            ended_at=TODAY + timedelta(days=25),
        )
        expired = Benefit.objects.create(
            applicant=self.a_dev, amount=9000,
            started_at=TODAY - timedelta(days=100),
            ended_at=TODAY - timedelta(days=10),
        )
        r = self.client.get('/api/v1/benefits/active/')
        ids = [b['id'] for b in r.data]
        self.assertIn(active.id, ids)
        self.assertNotIn(expired.id, ids)

    def test_unclosed_days(self):
        r = self.client.get('/api/v1/vacancies/unclosed_days/')
        ids = [v['id'] for v in r.data]
        self.assertNotIn(
            Vacancy.objects.filter(state='closed').first().id, ids
        )
        row = next(v for v in r.data if v['id'] == self.v_dev.id)
        self.assertEqual(row['days_open'], 20)

    def test_unrepresented_professions(self):
        Profession.objects.create(name='Космонавт')
        r = self.client.get('/api/v1/professions/unrepresented/')
        names = [p['name'] for p in r.data]
        self.assertIn('Космонавт', names)
        self.assertNotIn('Повар', names)

    def test_premium_vacancies(self):
        r = self.client.get('/api/v1/vacancies/premium/')
        ids = [v['id'] for v in r.data]
        self.assertIn(self.v_dev.id, ids)
        for v in r.data:
            self.assertEqual(v['education'], 'higher')
            self.assertGreaterEqual(float(v['salary']), 5000)
            self.assertLessEqual(float(v['salary']), 60000)

    def test_employers_report(self):
        r = self.client.get('/api/v1/employers/')
        row = next(e for e in r.data['results'] if e['name'].startswith('ООО «Металл»'))
        self.assertEqual(row['open_vacancies_count'], 1)

class CourseEnrollmentTests(APITestCase):
    def test_enrollment_with_grade(self):
        auth(self)
        (prof_cook, *_rest, a_cook, _a_dev) = base_data()
        course = Course.objects.create(
            name='Повар-кондитер', profession=prof_cook,
            started_at=TODAY - timedelta(days=100),
            ended_at=TODAY - timedelta(days=30),
        )
        r = self.client.post('/api/v1/enrollments/', {
            'applicant': a_cook.pk, 'course': course.pk,
            'enrolled_at': str(TODAY - timedelta(days=110)),
            'result_grade': 3,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Enrollment.objects.get(applicant=a_cook).result_grade, 3
        )

    def test_duplicate_enrollment_rejected(self):
        auth(self)
        (prof_cook, *_rest, a_cook, _a_dev) = base_data()
        course = Course.objects.create(
            name='Повар-кондитер', profession=prof_cook,
            started_at=TODAY, ended_at=TODAY + timedelta(days=30),
        )
        Enrollment.objects.create(
            applicant=a_cook, course=course, enrolled_at=TODAY,
        )
        r = self.client.post('/api/v1/enrollments/', {
            'applicant': a_cook.pk, 'course': course.pk,
            'enrolled_at': str(TODAY),
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

class VacancyMatchTests(APITestCase):
    def test_match_wrong_profession_rejected(self):
        auth(self)
        (prof_cook, prof_dev, _pw, _e1, _e2, _vc, _vd, _vp, a_cook, _ad) = base_data()
        wrong = Vacancy.objects.create(
            employer=Employer.objects.first(), profession=prof_dev,
            education='secondary', min_experience=0, salary=40000,
            posted_at=TODAY, state='open',
        )
        r = self.client.post('/api/v1/vacancy-matches/', {
            'applicant': a_cook.pk, 'vacancy': wrong.pk,
            'suggested_at': str(TODAY),
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_created(self):
        auth(self)
        (prof_cook, prof_dev, _pw, _e1, _e2, v_cook, _v_closed, _v_dev, a_cook, _a_dev) = base_data()
        r = self.client.post('/api/v1/vacancy-matches/', {
            'applicant': a_cook.pk, 'vacancy': v_cook.pk,
            'suggested_at': str(TODAY), 'accepted': True,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(VacancyMatch.objects.get(applicant=a_cook).accepted)
