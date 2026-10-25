from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Discipline, Homework, HomeworkSubmission

User = get_user_model()


class Command(BaseCommand):
    help = "Инициализация начальных демонстрационных данных для Доски домашних заданий (ЛР2)"

    def handle(self, *args, **options):
        self.stdout.write("Создание начальных данных...")

        # 1. Создание дисциплин
        disciplines_data = [
            ("Веб-программирование", "WEB-2026", "Курс по разработке сетевых приложений, Django, DRF и Vue.js"),
            ("Базы данных", "DB-2026", "Реляционные СУБД, нормализация данных, SQL, PostgreSQL"),
            ("Архитектура вычислительных систем", "ACS-2026", "Низкоуровневая архитектура, процессоры, память и сети"),
            ("Дискретная математика", "DM-2026", "Теория графов, логика и комбинаторика"),
        ]

        disciplines = {}
        for name, code, desc in disciplines_data:
            disc, created = Discipline.objects.get_or_create(
                name=name,
                defaults={"code": code, "description": desc},
            )
            disciplines[name] = disc
            if created:
                self.stdout.write(f"  + Дисциплина: {name}")

        # 2. Создание преподавателя (admin)
        teacher, created = User.objects.get_or_create(
            username="teacher",
            defaults={
                "first_name": "Антон",
                "last_name": "Говоров",
                "email": "teacher@itmo.ru",
                "role": "teacher",
                "class_group": "Факультет ПИН",
                "is_staff": True,
                "is_superuser": True,
                "bio": "Преподаватель дисциплины «Веб-программирование».",
            },
        )
        if created:
            teacher.set_password("admin123")
            teacher.save()
            self.stdout.write("  + Преподаватель / Администратор: teacher (пароль: admin123)")

        # 3. Создание учеников
        students_data = [
            ("tyunyaev", "Никита", "Тюняев", "tyunyaev@itmo.ru", "K3341"),
            ("ivanov", "Иван", "Иванов", "ivanov@itmo.ru", "K3341"),
            ("petrov", "Петр", "Петров", "petrov@itmo.ru", "K3341"),
            ("sidorov", "Алексей", "Сидоров", "sidorov@itmo.ru", "K3341"),
        ]

        students = {}
        for username, fname, lname, email, group in students_data:
            st, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                    "role": "student",
                    "class_group": group,
                    "bio": f"Студент группы {group}.",
                },
            )
            if created:
                st.set_password("password123")
                st.save()
                self.stdout.write(f"  + Ученик: {username} (пароль: password123)")
            students[username] = st

        # 4. Создание домашних заданий
        now = timezone.now().date()
        homeworks_data = [
            (
                disciplines["Веб-программирование"],
                "ЛР1: Сетевое взаимодействие на сокетах",
                now - timedelta(days=10),
                now + timedelta(days=5),
                "Реализовать UDP/TCP клиент-сервер, раздачу HTML-страницы по HTTP, многопользовательский чат и веб-сервер журнала оценок.",
                "Штраф: минус 1 балл за каждые полные сутки просрочки сдачи.",
            ),
            (
                disciplines["Веб-программирование"],
                "ЛР2: Веб-сервис на Django и PostgreSQL",
                now - timedelta(days=3),
                now + timedelta(days=12),
                "Разработать полнофункциональный сайт на Django с базой данных PostgreSQL в соответствии с вариантом №2 (Доска домашних заданий). Оформить отчёт в MkDocs.",
                "Штраф: минус 1 балл за каждые сутки опоздания.",
            ),
            (
                disciplines["Базы данных"],
                "SQL: Проектирование реляционной схемы",
                now - timedelta(days=14),
                now - timedelta(days=2),  # просрочено
                "Спроектировать ER-модель базы данных для образовательной платформы. Написать DDL-скрипты и составить 5 аналитических запросов с JOIN и GROUP BY.",
                "Штраф: максимум 4 балла при сдаче после дедлайна.",
            ),
            (
                disciplines["Дискретная математика"],
                "ДЗ: Алгоритмы на графах (Дейкстра, Флойд)",
                now - timedelta(days=2),
                now + timedelta(days=7),
                "Решить задачи по поиску кратчайших путей во взвешенных ориентированных графах. Привести пошаговые таблицы обхода.",
                "Без штрафа до окончания срока сдачи.",
            ),
        ]

        created_hws = []
        for subject, title, issue, due, desc, penalty in homeworks_data:
            hw, created = Homework.objects.get_or_create(
                title=title,
                defaults={
                    "subject": subject,
                    "teacher": teacher,
                    "issue_date": issue,
                    "due_date": due,
                    "description": desc,
                    "penalty_info": penalty,
                },
            )
            created_hws.append(hw)
            if created:
                self.stdout.write(f"  + ДЗ: {title}")

        # 5. Создание демонстрационных сдач и оценок
        submissions_data = [
            (
                created_hws[0],
                students["tyunyaev"],
                "Выполнена лабораторная работа №1 по сокетам. Все 5 заданий протестированы. Ссылка на репозиторий: github.com/NikitaTyunyaev/ITMO_ICT_WebDevelopment_2026-2027",
                5,
                "graded",
                "Отличная работа! Все протоколы реализованы корректно.",
            ),
            (
                created_hws[0],
                students["ivanov"],
                "Лабораторная работа выполнена. Проверена работа чата на нескольких терминалах.",
                5,
                "graded",
                "Принято на максимальный балл.",
            ),
            (
                created_hws[0],
                students["petrov"],
                "Сдаю задания 1-4 по сокетам, пятое задание дорабатывается.",
                4,
                "graded",
                "Хорошо, снижен 1 балл за неполный журнал оценок в задании 5.",
            ),
            (
                created_hws[0],
                students["sidorov"],
                "Отправляю решение практических заданий на сокетах на проверку.",
                None,
                "submitted",
                "",
            ),
            (
                created_hws[2],
                students["tyunyaev"],
                "Скрипты создания таблиц PostgreSQL и 5 запросов с индексами прикреплены.",
                5,
                "graded",
                "Отличный DDL скрипт, всё нормализовано до 3НФ.",
            ),
            (
                created_hws[2],
                students["ivanov"],
                "Запросы составлены, схема нормализована.",
                4,
                "graded",
                "Небольшая ошибка в внешнем ключе, но в целом хорошо.",
            ),
        ]

        for hw, student, text, grade, status, comment in submissions_data:
            sub, created = HomeworkSubmission.objects.get_or_create(
                homework=hw,
                student=student,
                defaults={
                    "answer_text": text,
                    "grade": grade,
                    "status": status,
                    "teacher_comment": comment,
                },
            )
            if created and grade:
                self.stdout.write(f"  + Оценка: {student.username} за {hw.title} -> {grade}")

        self.stdout.write(self.style.SUCCESS("Инициализация начальных данных успешно завершена!"))
