from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections, transaction
from django.test import TestCase, TransactionTestCase, Client
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from .models import Airline, Booking, Flight, Review
from .pagination import paginate, InvalidCursor


def make_flight(number='SU1', **changes):
    airline, _ = Airline.objects.get_or_create(code='SU', defaults={'name': 'Учебная авиакомпания'})
    now = timezone.now()
    values = dict(number=number, airline=airline, origin='Санкт-Петербург', destination='Москва',
                  departure_at=now + timedelta(days=3), arrival_at=now + timedelta(days=3, hours=2),
                  direction='departure', gate='A1', capacity=12)
    values.update(changes)
    return Flight.objects.create(**values)


class FlightFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('alice', password='ExamplePass123!', first_name='Анна', last_name='Соколова')
        self.other = User.objects.create_user('bob', password='ExamplePass123!')
        self.staff = User.objects.create_superuser('staff', password='ExamplePass123!')
        self.flight = make_flight()

    def book(self, user=None, seat=1):
        user = user or self.user
        return Booking.objects.create(flight=self.flight, user=user, passenger_name=str(user), seat=seat)

    def test_registration_login_and_jinja_rendering(self):
        response = self.client.post(reverse('register'), {'username': 'new-user', 'first_name': 'Новый',
            'last_name': 'Пассажир', 'email': 'test@example.org', 'password1': 'SafeFlightPass123!',
            'password2': 'SafeFlightPass123!'})
        self.assertRedirects(response, '/')
        self.assertTrue(get_user_model().objects.filter(username='new-user').exists())
        self.assertContains(self.client.get('/'), 'Новый Пассажир')
        self.client.post(reverse('logout'))
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertRedirects(self.client.post(reverse('login'), {'username': 'alice',
            'password': 'ExamplePass123!'}), '/')

    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse('booking_create', args=[self.flight.pk]), {'seat': 1, 'passenger_name': 'Анна'})
        self.assertEqual(response.status_code, 403)

    def test_booking_create_edit_delete_and_owner_access(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('booking_create', args=[self.flight.pk]), {'seat': 1, 'passenger_name': 'Анна'})
        self.assertRedirects(response, reverse('booking_list'))
        booking = Booking.objects.get(user=self.user)
        self.client.post(reverse('booking_edit', args=[booking.pk]), {'seat': 2, 'passenger_name': 'Анна Соколова'})
        booking.refresh_from_db()
        self.assertEqual(booking.seat, 2)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('booking_edit', args=[booking.pk]), {'seat': 3}).status_code, 404)
        self.assertEqual(self.client.post(reverse('booking_delete', args=[booking.pk])).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('booking_delete', args=[booking.pk])).status_code, 200)
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())
        self.client.post(reverse('booking_delete', args=[booking.pk]))
        self.assertFalse(Booking.objects.filter(pk=booking.pk).exists())

    def test_duplicates_capacity_and_closed_flights(self):
        self.book()
        with self.assertRaises(ValidationError):
            self.book(self.other, 1)
        with self.assertRaises(ValidationError):
            self.book(self.user, 2)
        with self.assertRaises(ValidationError):
            self.book(self.other, 99)
        self.flight.status = 'cancelled'
        self.flight.save()
        with self.assertRaises(ValidationError):
            self.book(self.other, 2)

    def test_checkin_requires_ticket_and_staff(self):
        booking = self.book()
        self.client.force_login(self.other)
        for path in [reverse('passengers', args=[self.flight.pk]), reverse('check_in', args=[booking.pk]),
                     reverse('flight_create'), reverse('flight_edit', args=[self.flight.pk])]:
            self.assertEqual(self.client.get(path).status_code, 403)
        booking.checked_in = True
        with self.assertRaises(ValidationError):
            booking.save()
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse('passengers', args=[self.flight.pk])), 'alice')
        self.assertRedirects(self.client.post(reverse('check_in', args=[booking.pk]), {'ticket_number': 'TICKET-1'}),
                             reverse('passengers', args=[self.flight.pk]))
        booking.refresh_from_db()
        self.assertTrue(booking.checked_in)
        self.client.force_login(self.user)
        self.client.post(reverse('booking_edit', args=[booking.pk]), {'seat': 2, 'passenger_name': 'x'})
        self.client.post(reverse('booking_delete', args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.seat, 1)

    def test_review_records_date_author_rating_and_escapes_html(self):
        self.client.force_login(self.user)
        endpoint = reverse('review_create', args=[self.flight.pk])
        self.assertEqual(self.client.get(endpoint).status_code, 403)
        self.book()
        self.assertEqual(self.client.post(endpoint, {'rating': 11, 'text': 'bad'}).status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.client.post(endpoint, {'rating': 8, 'text': '<script>alert(1)</script>'})
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.flight_date, timezone.localtime(self.flight.departure_at).date())
        response = self.client.get(self.flight.get_absolute_url())
        self.assertNotContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.client.post(endpoint, {'rating': 9, 'text': 'duplicate'})
        self.assertEqual(Review.objects.count(), 1)

    def test_filter_validation_search_and_admin_booking(self):
        self.assertContains(self.client.get('/?origin=Петербург&destination=Москва&q=SU1'), 'SU1')
        self.assertNotContains(self.client.get('/?origin=Казань'), 'SU1')
        self.assertEqual(self.client.get('/?date=not-a-date').status_code, 200)
        self.assertEqual(self.client.get('/?cursor=tampered').status_code, 200)
        self.client.force_login(self.staff)
        response = self.client.post('/admin/flights/booking/add/', {'flight': self.flight.pk,
            'user': self.other.pk, 'passenger_name': 'Боб', 'seat': 4, 'ticket_number': 'ADMIN-4',
            'checked_in': 'on', '_save': 'Сохранить'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.get(user=self.other).checked_in)

    def test_flight_admin_pages_and_validation(self):
        self.client.force_login(self.staff)
        for path in ['/admin/', '/admin/flights/flight/', '/admin/flights/booking/',
                     '/admin/accounts/user/', reverse('flight_create'), reverse('flight_edit', args=[self.flight.pk])]:
            self.assertEqual(self.client.get(path).status_code, 200)
        self.flight.arrival_at = self.flight.departure_at
        with self.assertRaises(ValidationError):
            self.flight.save()


class CursorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        at = timezone.now() + timedelta(days=5)
        for i in range(23):
            make_flight(f'SU{i}', departure_at=at, arrival_at=at + timedelta(hours=2))

    def test_equal_timestamps_forward_backward_and_no_offset(self):
        qs = Flight.objects.all()
        with CaptureQueriesContext(connection) as captured:
            first = paginate(qs, None, {})
            second = paginate(qs, first.next_cursor, {})
            third = paginate(qs, second.next_cursor, {})
            back = paginate(qs, third.previous_cursor, {})
        self.assertEqual([len(p.objects) for p in (first, second, third)], [10, 10, 3])
        ids = [f.pk for p in [first, second, third] for f in p]
        self.assertEqual(ids, list(qs.order_by('pk').values_list('pk', flat=True)))
        self.assertEqual([f.pk for f in back], [f.pk for f in second])
        self.assertIsNone(first.previous_cursor)
        self.assertIsNone(third.next_cursor)
        self.assertFalse(any('OFFSET' in query['sql'].upper() for query in captured))

    def test_tamper_filter_binding_expiry_and_insert(self):
        qs = Flight.objects.all()
        first = paginate(qs, None, {'q': 'SU'})
        for token, filters in [('forged', {'q': 'SU'}), (first.next_cursor, {'q': 'FV'})]:
            with self.assertRaises(InvalidCursor):
                paginate(qs, token, filters)
        with patch('django.core.signing.time.time', return_value=timezone.now().timestamp() + 86402):
            with self.assertRaises(InvalidCursor):
                paginate(qs, first.next_cursor, {'q': 'SU'})
        inserted = make_flight('NEW', departure_at=first.objects[-1].departure_at,
                               arrival_at=first.objects[-1].arrival_at)
        second = paginate(qs, first.next_cursor, {'q': 'SU'})
        third = paginate(qs, second.next_cursor, {'q': 'SU'})
        self.assertNotIn(inserted.pk, [f.pk for p in [second, third] for f in p])


class ConcurrentBookingTests(TransactionTestCase):
    def test_two_users_cannot_book_the_same_seat(self):
        flight = make_flight()
        users = [get_user_model().objects.create_user(f'racer{i}') for i in range(2)]
        barrier = Barrier(2)

        def reserve(user_id):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                Booking.objects.create(flight_id=flight.pk, user_id=user_id, passenger_name='Тест', seat=1)
                return True
            except ValidationError:
                return False
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reserve, [u.pk for u in users]))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(Booking.objects.filter(flight=flight, seat=1).count(), 1)
