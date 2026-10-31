"""Демо-данные для учебного проекта: python manage.py seed_demo.

Создаёт учителя, учеников с учебными группами, домашние задания и
сданные работы с выставленными отметками. Повторный запуск безопасен
(get_or_create) и добавляет только недостающие объекты.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from homework.models import Homework, Profile, Submission

STUDENTS = [
    ('ivan', 'student123', 'K3339'),
    ('maria', 'student123', 'K3339'),
    ('petr', 'student123', 'K3331'),
]

HOMEWORKS = [
    # (предмет, преподаватель, выдано дней назад, срок дней вперёд, текст, штрафы)
    ('Алгебра', 'Иванов И. И.', 9, 9, 'Вычислить определённые интегралы: ∫(2x+1)dx от 0 до 3.',
     'Штраф 30% от балла за сдачу после срока.'),
    ('Алгебра', 'Иванов И. И.', 8, 8, 'Решить систему линейных уравнений методом Крамера (два варианта).', ''),
    ('Физика', 'Петрова П. П.', 6, 12, 'Лабораторная работа: измерение ускорения свободного падения математическим маятником.',
     'Без штрафов.'),
    ('Информатика', 'Сидоров С. С.', 5, 14, 'Написать программу сортировки массива пузырьком на Python.',
     'Штраф 1 балл за каждый день опоздания.'),
    ('Информатика', 'Сидоров С. С.', 5, 14, 'Разработать ER-модель базы данных интернет-магазина.', ''),
    ('Английский', 'Кузнецова К. К.', 4, 16, 'Эссе на тему "Technology in education" (150–200 слов).', ''),
    ('История', 'Васильев В. В.', 3, 18, 'Таблица: реформы Петра I (дата, суть, последствия).',
     'При обнаружении копирования — 0 баллов.'),
    ('Химия', 'Смирнова С. С.', 2, 1, 'Решить задачи на закон сохранения массы. Варианты 1–5.', ''),
    ('Геометрия', 'Иванов И. И.', 1, 22, 'Доказать теорему о сумме углов треугольника.', ''),
]

SUBMISSIONS = [
    # (username, индекс задания, текст, отметка или None)
    ('ivan', 0, '∫(2x+1)dx = x² + x | от 0 до 3 = 9 + 3 = 12.', 5),
    ('ivan', 2, 'Провёл 20 измерений периода, g ≈ 9.81 м/с². Отчёт приложил.', None),
    ('maria', 0, 'Интеграл равен 12, подробное решение в приложении.', None),
    ('maria', 3, 'Написал программу сортировки пузырьком с комментариями, тесты пройдены.', 4),
    ('maria', 5, 'Эссе на 180 слов: технология ускоряет обучение, но требует баланса.', None),
    ('petr', 1, 'Метод Крамера: определители посчитаны, x = 2, y = -1.', None),
]


class Command(BaseCommand):
    help = 'Наполняет базу демонстрационными данными (учитель, ученики, задания, работы).'

    def handle(self, *args, **options):
        today = date.today()

        teacher, _ = User.objects.get_or_create(username='teacher')
        teacher.is_staff, teacher.is_superuser = True, True
        teacher.set_password('teacher123')
        teacher.save()

        for username, password, group in STUDENTS:
            user, _ = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.save()
            Profile.objects.update_or_create(user=user, defaults={'group': group})

        homeworks = []
        for subject, teacher_name, issued_ago, due_in, text, penalty in HOMEWORKS:
            # Ключ уникальности — (предмет, текст): у одного преподавателя может
            # быть несколько заданий по одному предмету, но текст задания уникален.
            hw, _ = Homework.objects.update_or_create(
                subject=subject,
                text=text,
                defaults={
                    'teacher': teacher_name,
                    'issue_date': today - timedelta(days=issued_ago),
                    'deadline': today + timedelta(days=due_in),
                    'penalty_info': penalty,
                },
            )
            homeworks.append(hw)

        created = 0
        for username, hw_index, text, mark in SUBMISSIONS:
            student = User.objects.get(username=username)
            homework = homeworks[hw_index]
            sub, was_created = Submission.objects.get_or_create(
                homework=homework, student=student,
                defaults={'text': text},
            )
            if mark is not None:
                sub.mark = mark
                sub.marked_at = timezone.now()
                sub.save()
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f'OK: заданий={Homework.objects.count()}, '
            f'пользователей={User.objects.count()}, '
            f'новых работ={created}'
        ))
