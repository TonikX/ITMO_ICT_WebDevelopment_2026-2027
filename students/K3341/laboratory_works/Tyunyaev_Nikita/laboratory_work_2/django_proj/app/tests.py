from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Discipline, Homework, HomeworkSubmission

User = get_user_model()


class HomeworkBoardTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Создаем дисциплину
        self.discipline = Discipline.objects.create(
            name="Веб-программирование",
            code="WEB",
            description="Курс по веб-разработке",
        )

        # Создаем преподавателя
        self.teacher = User.objects.create_user(
            username="teacher_test",
            password="password123",
            role="teacher",
            is_staff=True,
            first_name="Антон",
            last_name="Преподаватель",
        )

        # Создаем ученика
        self.student = User.objects.create_user(
            username="student_test",
            password="password123",
            role="student",
            first_name="Иван",
            last_name="Студент",
            class_group="K3341",
        )

        # Создаем домашнее задание
        self.homework = Homework.objects.create(
            subject=self.discipline,
            teacher=self.teacher,
            title="Тестовое ДЗ",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=7),
            description="Описание тестового задания",
            penalty_info="Штраф 1 балл в сутки",
        )

    def test_homework_list_view(self):
        """Проверка списка заданий и поиска"""
        response = self.client.get(reverse("homework_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовое ДЗ")
        self.assertContains(response, "Веб-программирование")

        # Проверка фильтрации
        response_filtered = self.client.get(reverse("homework_list"), {"subject": self.discipline.id})
        self.assertEqual(response_filtered.status_code, 200)
        self.assertContains(response_filtered, "Тестовое ДЗ")

        # Проверка поиска
        response_search = self.client.get(reverse("homework_list"), {"q": "Тестовое"})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, "Тестовое ДЗ")

    def test_homework_submission_by_student(self):
        """Проверка сдачи задания учеником"""
        self.client.login(username="student_test", password="password123")
        url = reverse("homework_submit", kwargs={"pk": self.homework.pk})

        response = self.client.post(url, {"answer_text": "Мое решение тестового задания"})
        self.assertEqual(response.status_code, 302)

        # Проверяем наличие сдачи в БД
        submission = HomeworkSubmission.objects.get(homework=self.homework, student=self.student)
        self.assertEqual(submission.answer_text, "Мое решение тестового задания")
        self.assertEqual(submission.status, "submitted")

    def test_teacher_grading_client(self):
        """Проверка выставления оценки преподавателем через клиентский интерфейс"""
        submission = HomeworkSubmission.objects.create(
            homework=self.homework,
            student=self.student,
            answer_text="Решение студента",
            status="submitted",
        )

        # Ученик не имеет права оценивать
        self.client.login(username="student_test", password="password123")
        grade_url = reverse("submission_grade", kwargs={"pk": submission.pk})
        res = self.client.post(grade_url, {"grade": 5, "status": "graded", "teacher_comment": "Отлично!"})
        submission.refresh_from_db()
        self.assertIsNone(submission.grade)

        # Преподаватель может оценить
        self.client.login(username="teacher_test", password="password123")
        res_teacher = self.client.post(grade_url, {"grade": 5, "status": "graded", "teacher_comment": "Отлично!"})
        self.assertEqual(res_teacher.status_code, 302)

        submission.refresh_from_db()
        self.assertEqual(submission.grade, 5)
        self.assertEqual(submission.status, "graded")
        self.assertEqual(submission.teacher_comment, "Отлично!")

    def test_gradebook_view(self):
        """Проверка классного журнала со сводной таблицей оценок"""
        HomeworkSubmission.objects.create(
            homework=self.homework,
            student=self.student,
            answer_text="Решение",
            grade=5,
            status="graded",
        )
        self.client.login(username="student_test", password="password123")
        response = self.client.get(reverse("gradebook"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сводная ведомость оценок")
        self.assertContains(response, "Студент")
        self.assertContains(response, "5")
