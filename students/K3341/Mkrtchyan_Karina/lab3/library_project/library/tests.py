from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from . import models


class LibraryAPITests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(username='librarian', is_staff=True)
        self.client.force_authenticate(self.staff)
        self.section = models.Section.objects.create(name='Fiction')
        self.publisher = models.Publisher.objects.create(name='Press')
        self.author = models.Author.objects.create(full_name='Author')

    def create(self, endpoint, **data):
        result = self.client.post(f'/api/{endpoint}/', data, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        return result.data

    def book_and_copy(self):
        book = self.create('books', title='Book', publication_year=2000,
                           publisher=self.publisher.pk, section=self.section.pk,
                           author_ids=[self.author.pk])
        copy = self.create('copies', book=book['id_book'], inventory_no='INV-1', acquired_at='2024-01-01')
        return book['id_book'], copy['id_copy']

    def reader(self):
        return self.create('readers', full_name='Reader', passport_no='TEST', birth_date='2010-01-01',
                           address='Test address', education='SECONDARY', registered_at='2024-02-01')['id_reader']

    def test_auth_flow(self):
        self.client.force_authenticate(None)
        credentials = {'username': 'newuser', 'password': 'A!good-passphrase-859'}
        self.assertEqual(self.client.post('/auth/users/', credentials).status_code, 201)
        token = self.client.post('/auth/token/login/', credentials).data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.get('/auth/users/me/').data['username'], 'newuser')
        self.assertEqual(self.client.get('/api/books/').status_code, 200)
        self.assertEqual(self.client.get('/api/readers/').status_code, 403)
        self.assertEqual(self.client.post('/api/authors/', {'full_name': 'Denied'}).status_code, 403)
        self.assertEqual(self.client.post('/auth/token/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/books/').status_code, 401)

    def test_nested_crud_and_protected_delete(self):
        book, copy = self.book_and_copy()
        url = f'/api/books/{book}/'
        data = self.client.get(url).data
        self.assertEqual(data['authors'][0]['id_author'], self.author.pk)
        self.assertEqual(data['copies'][0]['id_copy'], copy)
        self.assertEqual(self.client.patch(url, {'author_ids': []}, format='json').data['authors'], [])
        self.assertEqual(self.client.delete(url).status_code, 409)
        self.assertEqual(self.client.delete(f'/api/copies/{copy}/').status_code, 204)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_loan_reports_and_expired_readers(self):
        _, copy = self.book_and_copy()
        reader = self.reader()
        data = dict(copy=copy, reader=reader, issued_at='2024-02-02T10:00:00Z', due_at='2024-02-10T10:00:00Z')
        loan = self.create('loans', **data)['id_loan']
        self.assertEqual(self.client.post('/api/loans/', data, format='json').status_code, 400)
        for url in (f'/api/readers/{reader}/current-books/', '/api/reports/loans-older-than-month/',
                    '/api/reports/rare-book-loans/'):
            self.assertEqual(self.client.get(url).data[0]['id_loan'], loan)
        self.assertEqual(self.client.get('/api/reports/reader-demographics/').data['education_percent']['SECONDARY'], 100)
        self.assertEqual(self.client.get('/api/reports/readers-under-20/').data['reader_count'],
                         int(timezone.localdate().year < 2030))
        self.assertEqual(self.client.post('/api/readers/deregister-expired/').data['deregistered_count'], 1)
        self.assertEqual(self.client.get('/api/reports/reader-demographics/').data['reader_count'], 0)
        response = self.client.patch(f'/api/loans/{loan}/', {'returned_at': '2024-02-03T10:00:00Z'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/reports/rare-book-loans/').data, [])

    def test_monthly_report_uses_history(self):
        _, copy = self.book_and_copy()
        reader = self.reader()
        first = models.ReadingRoom.objects.create(room_number='1', name='First', capacity=10)
        second = models.ReadingRoom.objects.create(room_number='2', name='Second', capacity=10)
        for room, day in ((first, '2024-02-01'), (second, '2024-02-02')):
            self.create('copy-rooms', copy=copy, room=room.pk, valid_from=f'{day}T11:00:00Z')
            self.create('reader-rooms', reader=reader, room=room.pk, valid_from=day)
        response = self.client.get('/api/reports/monthly/?month=2024-02')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['days']), 29)
        for i, expected in enumerate(([1, 0], [0, 1])):
            rooms = response.data['days'][i]['rooms']
            self.assertEqual([room['copy_count'] for room in rooms], expected)
            self.assertEqual([room['reader_count'] for room in rooms], expected)
        self.assertEqual([room['reader_count'] for room in response.data['registrations']['rooms']], [1, 0])
        self.assertEqual(self.client.get('/api/reports/monthly/?month=2024-13').status_code, 400)
