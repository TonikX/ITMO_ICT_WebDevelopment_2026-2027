from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tasks.models import StudentProfile, Task, Work


class Command(BaseCommand):
    help = 'Наполняет базу демонстрационными данными'

    def handle(self, *args, **options):
        teacher, _ = User.objects.get_or_create(
            username='anna',
            is_staff=True,
            is_superuser=True,
            defaults={'first_name': 'Анна Петровна'},
        )
        teacher.set_password('anna12345')
        teacher.save()

        students = {}
        for login, fio, group in [
            ('oleg', 'Олег Кузнецов', 'K3339'),
            ('kate', 'Катя Соколова', 'K3339'),
            ('dima', 'Дима Орлов', 'K3340'),
        ]:
            u, _ = User.objects.get_or_create(username=login, defaults={'first_name': fio})
            u.set_password('pass12345')
            u.save()
            StudentProfile.objects.update_or_create(user=u, defaults={'study_group': group})
            students[login] = u

        today = date.today()
        tasks_data = [
            ('Информатика', 'Смирнова А.П.', 'Написать программу-калькулятор на Python', '-1 балл за день просрочки'),
            ('Физика', 'Гусев В.В.', 'Решить 10 задач на движение по окружности', ''),
            ('Литература', 'Ильина М.Ю.', 'Прочитать рассказ и написать отзыв на страницу', 'отметка снижается на 1'),
            ('Геометрия', 'Панов К.С.', 'Доказать теорему о вписанном угле', ''),
            ('Информатика', 'Смирнова А.П.', 'Составить блок-схему алгоритма сортировки', ''),
            ('Физика', 'Гусев В.В.', 'Подготовить доклад про электрический ток', '-2 балла за неделю'),
            ('Химия', 'Фомина Е.Б.', 'Выучить таблицу растворимости', ''),
            ('Литература', 'Ильина М.Ю.', 'Выучить наизусть стихотворение', ''),
            ('Геометрия', 'Панов К.С.', 'Построить сечения куба', ''),
        ]
        tasks = []
        for i, (disc, teacher_name, body, penalty) in enumerate(tasks_data):
            t, _ = Task.objects.get_or_create(
                discipline=disc,
                teacher_name=teacher_name,
                body=body,
                defaults={
                    'issued_on': today - timedelta(days=i + 1),
                    'due_on': today + timedelta(days=i % 5 + 1),
                    'penalty': penalty,
                },
            )
            tasks.append(t)

        works_data = [
            ('oleg', 0, 'Готово, калькулятор умеет четыре действия', 5),
            ('oleg', 1, 'Решил 8 из 10, последние не успел', None),
            ('kate', 0, 'Сделала с функциями и циклом while', 4),
            ('kate', 2, 'Отзыв на две страницы приложен', None),
            ('kate', 4, 'Блок-схема в приложении', 5),
            ('dima', 1, 'Задачи решены, расписала ход решения', 3),
        ]
        created = 0
        for login, task_idx, body, score in works_data:
            _, created_flag = Work.objects.get_or_create(
                task=tasks[task_idx],
                student=students[login],
                defaults={'body': body, 'score': score},
            )
            created += int(created_flag)

        self.stdout.write(self.style.SUCCESS(
            f'Готово: заданий={Task.objects.count()}, учеников={len(students)}, работ={Work.objects.count()}'
        ))
