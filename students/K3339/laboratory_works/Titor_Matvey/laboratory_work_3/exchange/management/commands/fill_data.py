from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from exchange.models import (Applicant, Benefit, Course, Employer, Enrollment,
                             Profession, Vacancy, VacancyMatch, WorkExperience)

class Command(BaseCommand):
    help = 'Наполняет базу демонстрационными данными'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username='admin', is_staff=True, is_superuser=True,
        )
        admin.set_password('admin12345')
        admin.save()

        professions = {}
        for name in ['Повар', 'Программист', 'Сварщик', 'Бухгалтер', 'Водитель']:
            p, _ = Profession.objects.get_or_create(name=name)
            professions[name] = p

        employers = {}
        for name, addr, person, phone in [
            ('ООО «Колбасы и сыры»', 'СПб, Лиговский пр., 50', 'Ирина Соколова', '+7 812 100-11-22'),
            ('ООО «Код и кофе»', 'СПб, ул. Рубинштейна, 3', 'Павел Крылов', '+7 812 200-22-33'),
            ('АО «Завод Молот»', 'СПб, Свердловская наб., 12', 'Ольга Тихонова', '+7 812 300-33-44'),
            ('ООО «СчётСервис»', 'СПб, Невский пр., 100', 'Денис Белов', '+7 812 400-44-55'),
            ('ООО «Дальнобой»', 'СПб, Московское ш., 25', 'Мария Ефимова', '+7 812 500-55-66'),
        ]:
            e, _ = Employer.objects.get_or_create(
                name=name,
                defaults={'address': addr, 'contact_person': person, 'phone': phone},
            )
            employers[name] = e

        today = date.today()
        vacancies_data = [
            ('ООО «Колбасы и сыры»', 'Повар', 'secondary', 2, 3, 55000, today - timedelta(days=45), 'open'),
            ('ООО «Колбасы и сыры»', 'Повар', 'primary', 0, None, 40000, today - timedelta(days=10), 'closed'),
            ('ООО «Код и кофе»', 'Программист', 'higher', 3, 4, 58000, today - timedelta(days=20), 'open'),
            ('АО «Завод Молот»', 'Сварщик', 'vocational', 1, 2, 60000, today - timedelta(days=7), 'open'),
            ('ООО «СчётСервис»', 'Бухгалтер', 'higher', 5, None, 59000, today - timedelta(days=90), 'offered'),
            ('ООО «Дальнобой»', 'Водитель', 'secondary', 4, None, 45000, today - timedelta(days=2), 'open'),
        ]
        vacancies = []
        for emp, prof, edu, exp, grade, salary, posted, state in vacancies_data:
            v, _ = Vacancy.objects.get_or_create(
                employer=employers[emp],
                profession=professions[prof],
                posted_at=posted,
                defaults={
                    'education': edu, 'min_experience': exp, 'grade': grade,
                    'salary': salary, 'state': state,
                },
            )
            vacancies.append(v)

        applicants_data = [
            ('Кузнецов Олег Викторович', date(1998, 4, 12), '7800 123456', 'higher', 'Программист', 3, 4, 52000, today - timedelta(days=30)),
            ('Соколова Анна Павловна', date(2001, 9, 3), '7800 654321', 'secondary', 'Повар', 2, 1, 33000, today - timedelta(days=15)),
            ('Ефремов Денис Игоревич', date(1995, 1, 27), '7800 111222', 'vocational', 'Сварщик', 3, 5, 58000, today - timedelta(days=60)),
            ('Морозова Вера Сергеевна', date(2003, 6, 18), '7800 333444', 'secondary', 'Бухгалтер', None, 0, None, today - timedelta(days=5)),
            ('Громов Иван Андреевич', date(1990, 11, 8), '7800 555666', 'secondary', 'Водитель', 4, 10, 48000, today - timedelta(days=100)),
        ]
        applicants = []
        for fio, born, passport, edu, prof, grade, exp, salary, reg in applicants_data:
            a, _ = Applicant.objects.get_or_create(
                passport=passport,
                defaults={
                    'full_name': fio, 'birth_date': born, 'education': edu,
                    'profession': professions[prof], 'grade': grade,
                    'experience_years': exp, 'last_salary': salary, 'registered_at': reg,
                },
            )
            applicants.append(a)

        work_data = [
            (0, 'Яндекс', 'Junior-разработчик', date(2021, 6, 1), date(2024, 5, 30)),
            (0, 'ООО «СофтЛайн»', 'Стажёр', date(2020, 8, 1), date(2021, 5, 15)),
            (1, 'Кафе «Балкон»', 'Повар-универсал', date(2023, 2, 1), None),
            (2, 'АО «Прометей»', 'Сварщик 3 разряда', date(2019, 3, 1), date(2025, 1, 10)),
            (4, 'ООО «ТрансЛогистик»', 'Водитель категории E', date(2015, 4, 1), None),
        ]
        for idx, company, pos, start, end in work_data:
            WorkExperience.objects.get_or_create(
                applicant=applicants[idx], company=company, position=pos,
                defaults={'started_at': start, 'ended_at': end},
            )

        Benefit.objects.get_or_create(
            applicant=applicants[1],
            defaults={'amount': 9900, 'started_at': today - timedelta(days=10),
                      'ended_at': today + timedelta(days=80)},
        )
        Benefit.objects.get_or_create(
            applicant=applicants[3],
            defaults={'amount': 12400, 'started_at': today - timedelta(days=200),
                      'ended_at': today - timedelta(days=20)},
        )

        courses_data = [
            ('Повар-кондитер', 'Повар', today - timedelta(days=120), today - timedelta(days=30)),
            ('Python для профи', 'Программист', today - timedelta(days=15), today + timedelta(days=60)),
            ('Сварщик 4 разряда', 'Сварщик', today + timedelta(days=10), today + timedelta(days=90)),
        ]
        courses = []
        for name, prof, start, end in courses_data:
            c, _ = Course.objects.get_or_create(
                name=name, profession=professions[prof],
                defaults={'started_at': start, 'ended_at': end},
            )
            courses.append(c)

        Enrollment.objects.get_or_create(
            applicant=applicants[0], course=courses[1],
            defaults={'enrolled_at': today - timedelta(days=10)},
        )
        Enrollment.objects.get_or_create(
            applicant=applicants[1], course=courses[0],
            defaults={'enrolled_at': today - timedelta(days=110), 'result_grade': 3},
        )

        VacancyMatch.objects.get_or_create(
            applicant=applicants[0], vacancy=vacancies[2],
            defaults={'suggested_at': today - timedelta(days=3), 'accepted': True},
        )
        VacancyMatch.objects.get_or_create(
            applicant=applicants[2], vacancy=vacancies[3],
            defaults={'suggested_at': today - timedelta(days=1)},
        )

        self.stdout.write(self.style.SUCCESS(
            f'Готово: профессий={Profession.objects.count()}, вакансий={Vacancy.objects.count()}, '
            f'соискателей={Applicant.objects.count()}, курсов={Course.objects.count()}'
        ))
