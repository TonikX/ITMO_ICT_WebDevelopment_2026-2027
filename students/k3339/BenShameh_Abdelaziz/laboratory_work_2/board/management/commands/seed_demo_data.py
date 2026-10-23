import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from board.models import Subject, Homework


class Command(BaseCommand):
    """
    Run with: python manage.py seed_demo_data
    Creates a couple of demo students, subjects and homeworks so the
    site isn't empty on first run. Safe to run more than once --
    get_or_create() means it won't create duplicates.
    """
    help = "Creates demo students, subjects and homeworks"

    def handle(self, *args, **options):
        if not User.objects.filter(username='alice').exists():
            User.objects.create_user('alice', password='AlicePass123')
            self.stdout.write("Created student 'alice' / AlicePass123")

        if not User.objects.filter(username='bob').exists():
            User.objects.create_user('bob', password='BobPass123')
            self.stdout.write("Created student 'bob' / BobPass123")

        math, _ = Subject.objects.get_or_create(name='Mathematics')
        physics, _ = Subject.objects.get_or_create(name='Physics')
        history, _ = Subject.objects.get_or_create(name='History')

        Homework.objects.get_or_create(
            subject=math, teacher_name='Mrs. Ivanova',
            date_given=datetime.date(2026, 10, 1), deadline=datetime.date(2026, 10, 30),
            text='Solve exercises 1-10 from chapter 3', penalty_info='-10% per day late'
        )
        Homework.objects.get_or_create(
            subject=physics, teacher_name='Mr. Petrov',
            date_given=datetime.date(2026, 10, 5), deadline=datetime.date(2026, 11, 5),
            text='Lab report on pendulum experiment', penalty_info='No late submissions accepted'
        )
        Homework.objects.get_or_create(
            subject=history, teacher_name='Mrs. Orlova',
            date_given=datetime.date(2026, 10, 10), deadline=datetime.date(2026, 11, 1),
            text='Essay on the causes of World War I (500 words)', penalty_info=''
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
