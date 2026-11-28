from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from library import models as m
from library.reporting import midnight


class Command(BaseCommand):
    help = 'Adds fictional library records for demonstrating the reports.'

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        room_a, room_b = [m.ReadingRoom.objects.get_or_create(
            room_number=f'DEMO-{code}', defaults={'name': name, 'capacity': 20},
        )[0] for code, name in [('A', 'Демо: общий зал'), ('B', 'Демо: тихий зал')]]
        section, _ = m.Section.objects.get_or_create(name='Демо: художественная литература')
        publisher, _ = m.Publisher.objects.get_or_create(name='Демо: издательство')
        author, _ = m.Author.objects.get_or_create(full_name='Демо: автор')
        readers = []
        for i, (name, age, education, registered, room) in enumerate([
            ('Анна Примерова', 18, 'SECONDARY', today - timedelta(days=90), room_a),
            ('Борис Примеров', 36, 'HIGHER', today.replace(day=1), room_b),
            ('Вера Примерова', 50, 'PRIMARY', today - timedelta(days=500), room_a),
        ], 1):
            reader, _ = m.Reader.objects.get_or_create(passport_no=f'LAB3-DEMO-{i}', defaults={
                'full_name': name, 'birth_date': today - timedelta(days=365 * age),
                'address': 'Демо: вымышленный адрес', 'education': education,
                'registered_at': registered, 'has_degree': i == 2,
            })
            readers.append(reader)
            m.ReaderTicketHistory.objects.get_or_create(ticket_no=f'LAB3-DEMO-{i}', defaults={
                'reader': reader, 'valid_from': reader.registered_at,
            })
            m.ReaderRoomHistory.objects.get_or_create(
                reader=reader, valid_from=reader.registered_at, defaults={'room': room},
            )

        anchor = readers[0].registered_at
        month_start = readers[1].registered_at
        for i, (title, quantity) in enumerate([('Демо: редкое издание', 2), ('Демо: популярное издание', 3)], 1):
            book, _ = m.Book.objects.get_or_create(title=title, section=section, publisher=publisher,
                                                   defaults={'publication_year': 2020})
            book.authors.add(author)
            m.BookCipherHistory.objects.get_or_create(book=book, cipher=f'LAB3-DEMO-{i}',
                                                       defaults={'valid_from': anchor})
            for j in range(1, quantity + 1):
                copy, _ = m.BookCopy.objects.get_or_create(inventory_no=f'LAB3-DEMO-{i}-{j}', defaults={
                    'book': book, 'acquired_at': anchor,
                })
                m.CopyRoomHistory.objects.get_or_create(copy=copy, valid_from=midnight(anchor),
                                                        defaults={'room': room_a})
                if j == 2:
                    m.CopyRoomHistory.objects.get_or_create(copy=copy, valid_from=midnight(month_start),
                                                            defaults={'room': room_b})
                if j == 1:
                    issued = midnight(anchor + timedelta(days=10))
                    m.Loan.objects.get_or_create(copy=copy, issued_at=issued, defaults={
                        'reader': readers[0], 'due_at': issued + timedelta(days=14),
                        'returned_at': None if i == 1 else issued + timedelta(days=7),
                    })
        self.stdout.write(self.style.SUCCESS(
            f'Демо-данные готовы. Читатель с открытой выдачей: ID {readers[0].pk}. '
            f'Месяц для отчёта: {month_start:%Y-%m}.',
        ))
