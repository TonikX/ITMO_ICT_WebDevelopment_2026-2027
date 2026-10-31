"""Тесты (django.test.TestCase) для приложения "Доска домашних заданий"."""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.paginator import Page
from django.test import TestCase

from .models import Homework, Profile, Submission


class SetupMixin:
    """Общие данные: учитель, ученики, задания, работы."""

    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user(
            username='teacher', password='pass', is_staff=True, is_superuser=True,
        )
        cls.ivan = User.objects.create_user(username='ivan', password='pass')
        cls.maria = User.objects.create_user(username='maria', password='pass')
        Profile.objects.create(user=cls.ivan, group='K3339')
        Profile.objects.create(user=cls.maria, group='K3339')

        cls.hw_algebra = Homework.objects.create(
            subject='Алгебра', teacher='Иванов И. И.',
            issue_date=date.today() - timedelta(days=7),
            deadline=date.today() + timedelta(days=7),
            text='Вычислить интегралы.', penalty_info='Штраф за опоздание.',
        )
        cls.hw_physics = Homework.objects.create(
            subject='Физика', teacher='Петрова П. П.',
            issue_date=date.today() - timedelta(days=3),
            deadline=date.today() + timedelta(days=10),
            text='Лабораторная работа по маятнику.', penalty_info='',
        )


class IndexViewTests(SetupMixin, TestCase):

    def test_index_returns_200_and_lists_homeworks(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вычислить интегралы')
        self.assertContains(response, 'Лабораторная работа')

    def test_filters_by_subject(self):
        response = self.client.get('/', {'subject': 'Алгебра'})
        self.assertContains(response, 'Вычислить интегралы')
        self.assertNotContains(response, 'Лабораторная работа')

    def test_search_by_text_and_teacher(self):
        response = self.client.get('/', {'q': 'маятник'})
        self.assertContains(response, 'Лабораторная работа')
        self.assertNotContains(response, 'Вычислить интегралы')
        response = self.client.get('/', {'q': 'Петрова'})
        self.assertContains(response, 'Лабораторная работа')

    def test_pagination(self):
        # Добавляем ещё заданий, чтобы страниц стало больше одной.
        for i in range(6):
            Homework.objects.create(
                subject='Доп', teacher=f'Учитель {i}', text=f'Задание номер {i}',
                issue_date=date.today(), deadline=date.today() + timedelta(days=30),
            )
        response = self.client.get('/')
        page = response.context['pages']
        self.assertIsInstance(page, Page)
        self.assertGreater(page.paginator.num_pages, 1)


class DetailViewTests(SetupMixin, TestCase):

    def test_anonymous_sees_authorization_hint(self):
        response = self.client.get(f'/homework/{self.hw_algebra.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'зарегистрируйтесь')

    def test_student_submits_solution(self):
        self.client.login(username='ivan', password='pass')
        response = self.client.post(
            f'/homework/{self.hw_algebra.pk}/',
            {'action': 'submit', 'text': 'Моё решение: 12'},
        )
        self.assertRedirects(response, f'/homework/{self.hw_algebra.pk}/')
        self.assertTrue(
            Submission.objects.filter(homework=self.hw_algebra, student=self.ivan).exists()
        )

    def test_duplicate_submission_is_rejected(self):
        self.client.login(username='ivan', password='pass')
        self.client.post(
            f'/homework/{self.hw_algebra.pk}/',
            {'action': 'submit', 'text': 'первый ответ'},
        )
        response = self.client.post(
            f'/homework/{self.hw_algebra.pk}/',
            {'action': 'submit', 'text': 'второй ответ'},
        )
        # Повторная форма не создаёт новую работу.
        self.assertEqual(
            Submission.objects.filter(homework=self.hw_algebra, student=self.ivan).count(),
            1,
        )

    def test_teacher_sees_all_submissions(self):
        Submission.objects.create(homework=self.hw_algebra, student=self.ivan, text='Иван: ответ')
        Submission.objects.create(homework=self.hw_algebra, student=self.maria, text='Мария: ответ')
        self.client.login(username='teacher', password='pass')
        response = self.client.get(f'/homework/{self.hw_algebra.pk}/')
        self.assertContains(response, 'Сданные работы: 2')
        self.assertContains(response, 'Иван: ответ')
        self.assertContains(response, 'Мария: ответ')


class RegistrationTests(TestCase):

    def test_register_creates_user_with_group(self):
        response = self.client.post('/register/', {
            'username': 'sveta',
            'group': 'K3339',
            'password1': 'Qwerty123!',
            'password2': 'Qwerty123!',
        })
        self.assertRedirects(response, '/accounts/login/')
        user = User.objects.get(username='sveta')
        self.assertEqual(user.profile.group, 'K3339')
        self.assertFalse(user.is_staff)

    def test_register_rejects_weak_password(self):
        response = self.client.post('/register/', {
            'username': 'bad', 'group': '', 'password1': '1', 'password2': '1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


class MySubmissionsTests(SetupMixin, TestCase):

    def test_requires_login(self):
        response = self.client.get('/my/')
        self.assertEqual(response.status_code, 302)

    def test_shows_own_submissions_with_mark(self):
        submission = Submission.objects.create(
            homework=self.hw_algebra, student=self.ivan, text='ответ ивана',
        )
        submission.mark = 5
        submission.save()
        self.client.login(username='ivan', password='pass')
        response = self.client.get('/my/')
        self.assertContains(response, 'ответ ивана')
        self.assertContains(response, '5')


class ClassSummaryTests(SetupMixin, TestCase):

    def test_anonymous_does_not_crash(self):
        response = self.client.get('/summary/')
        self.assertEqual(response.status_code, 200)

    def test_student_sees_only_their_class(self):
        Submission.objects.create(homework=self.hw_algebra, student=self.ivan, text='иван')
        Submission.objects.create(homework=self.hw_physics, student=self.ivan, text='иван2')
        self.client.login(username='ivan', password='pass')
        response = self.client.get('/summary/')
        self.assertEqual(response.status_code, 200)
        # Ивановой учебной группе K3339 соответствует две сданные работы.
        self.assertContains(response, '2')

    def test_teacher_can_switch_group(self):
        Submission.objects.create(homework=self.hw_algebra, student=self.ivan, text='иван')
        self.client.login(username='teacher', password='pass')
        response = self.client.get('/summary/', {'group': 'K3339'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сводка по всем классам')
