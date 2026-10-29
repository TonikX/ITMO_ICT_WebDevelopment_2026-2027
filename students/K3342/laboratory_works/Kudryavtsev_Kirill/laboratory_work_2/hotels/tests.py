from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from .models import Booking, Hotel, Review, Room


class HotelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('anna', 'anna@example.test', 'Strong-test-pass-91')
        self.other = User.objects.create_user('bob', password='Strong-test-pass-92')
        self.staff = User.objects.create_superuser('staff', 'staff@example.test', 'Strong-test-pass-93')
        self.hotel = Hotel.objects.create(name='Северный двор', city='Санкт-Петербург', owner='ООО Север', address='Литейный, 18', description='Тихий отель')
        self.room = Room.objects.create(hotel=self.hotel, number='101', room_type='double', price=4200, capacity=2, amenities='Wi-Fi')
        self.today = timezone.localdate()
        self.client.force_login(self.user)

    def booking(self, **kwargs):
        data = dict(room=self.room, user=self.user, arrival=self.today, departure=self.today+timedelta(days=2), guests=1)
        data.update(kwargs)
        return Booking.objects.create(**data)

    def dates(self, a=1, d=3, guests=1):
        return dict(arrival=str(self.today+timedelta(days=a)), departure=str(self.today+timedelta(days=d)), guests=guests)

    def test_registration_login_and_post_logout(self):
        c = Client()
        response = c.post(reverse('register'), dict(username='newguest', first_name='Ирина', last_name='Петрова', email='irina@example.test', password1='QwEr-strong-9123', password2='QwEr-strong-9123'))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newguest')
        self.assertTrue(user.check_password('QwEr-strong-9123'))
        self.assertFalse(user.is_staff)
        self.assertEqual(c.get(reverse('logout')).status_code, 405)
        c.post(reverse('logout'))
        self.assertEqual(c.get(reverse('my_bookings')).status_code, 302)
        self.assertEqual(c.post(reverse('login'), {'username': 'newguest', 'password': 'QwEr-strong-9123'}).status_code, 302)

    def test_booking_create_edit_delete_and_permissions(self):
        response = self.client.post(reverse('booking_create', args=[self.room.pk]), self.dates())
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.client.force_login(self.other)
        for name in ['booking_edit', 'booking_delete', 'review_create']:
            self.assertEqual(self.client.post(reverse(name, args=[booking.pk]), self.dates()).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('booking_edit', args=[booking.pk]), self.dates(3, 5, 2)).status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.guests, 2)
        self.assertEqual(booking.total, 8400)
        self.assertEqual(self.client.get(reverse('booking_delete', args=[booking.pk])).status_code, 200)
        self.assertTrue(Booking.objects.exists())
        self.client.post(reverse('booking_delete', args=[booking.pk]))
        self.assertFalse(Booking.objects.exists())

    def test_booking_validation_and_adjacent_dates(self):
        self.booking()
        for data in [self.dates(1, 3), self.dates(2, 1), self.dates(-1, 1), self.dates(3, 5, 3), self.dates(3, 5, 0)]:
            response = self.client.post(reverse('booking_create', args=[self.room.pk]), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(self.client.post(reverse('booking_create', args=[self.room.pk]), self.dates(2, 4)).status_code, 302)
        self.assertEqual(Booking.objects.count(), 2)

    def test_staff_transitions_in_browser_and_admin(self):
        b = self.booking()
        url = reverse('staff_action', args=[b.pk, 'checkin'])
        self.assertEqual(self.client.post(url).status_code, 403)
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.BOOKED)
        self.assertNotContains(self.client.get(reverse('room_list')), 'Заселение</a>')
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse('staff_bookings')), 'Заселить')
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.IN)
        self.assertIsNotNone(b.checked_in_at)
        self.client.post(reverse('admin:hotels_booking_changelist'), {'action': 'check_out', '_selected_action': str(b.pk)})
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.OUT)
        self.assertIsNotNone(b.checked_out_at)
        for name in ['booking_edit', 'booking_delete']:
            self.client.force_login(self.user)
            self.assertEqual(self.client.post(reverse(name, args=[b.pk]), self.dates()).status_code, 404)

    def test_checkin_outside_dates_and_double_transition(self):
        b = self.booking(arrival=self.today+timedelta(days=1), departure=self.today+timedelta(days=3))
        with self.assertRaises(ValidationError):
            b.change_status('checkin')
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.BOOKED)
        with self.assertRaises(ValidationError):
            b.change_status('checkout')

    def test_reviews_ownership_rating_dates_duplicate_and_html(self):
        b = self.booking()
        url = reverse('review_create', args=[b.pk])
        self.assertEqual(self.client.post(url, {'rating': 8, 'text': 'Хорошо'}).status_code, 404)
        b.change_status('checkin')
        b.change_status('checkout')
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, {'rating': 8, 'text': 'Чужой'}).status_code, 404)
        self.client.force_login(self.user)
        for rating in [0, 11]:
            self.assertEqual(self.client.post(url, {'rating': rating, 'text': 'Отзыв'}).status_code, 200)
            self.assertFalse(Review.objects.exists())
        self.assertEqual(self.client.post(url, {'rating': 9, 'text': '<script>alert(1)</script>'}).status_code, 302)
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.arrival, self.today)
        self.client.post(url, {'rating': 10, 'text': 'Повтор'})
        self.assertEqual(Review.objects.count(), 1)
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_guests_last_month_overlap_and_staff_only(self):
        now = timezone.now()
        recent = self.booking(status=Booking.OUT, checked_in_at=now-timedelta(days=40), checked_out_at=now-timedelta(days=10))
        old = self.booking(room=self.room, user=self.other, status=Booking.OUT, checked_in_at=now-timedelta(days=50), checked_out_at=now-timedelta(days=40))
        self.booking(arrival=self.today+timedelta(days=3), departure=self.today+timedelta(days=5))
        self.assertEqual(self.client.get(reverse('guests')).status_code, 403)
        self.client.force_login(self.staff)
        response = self.client.get(reverse('guests'))
        self.assertContains(response, timezone.localtime(recent.checked_in_at).strftime('%d.%m.%Y %H:%M'))
        self.assertNotContains(response, timezone.localtime(old.checked_in_at).strftime('%d.%m.%Y %H:%M'))
        self.assertNotContains(response, '>bob<')

    def test_search_pagination_available_dates_and_bad_input(self):
        for i in range(2, 10):
            Room.objects.create(hotel=self.hotel, number=str(i), room_type='single', price=2000, capacity=1, amenities='Душ')
        self.booking()
        response = self.client.get(reverse('room_list'))
        self.assertContains(response, '9 найдено')
        self.assertContains(response, '<article class="card">', count=6)
        response = self.client.get(reverse('room_list'), {'q': 'петербург', 'room_type': 'single', 'page': 2})
        self.assertContains(response, '<article class="card">', count=2)
        self.assertContains(response, 'room_type=single')
        response = self.client.get(reverse('room_list'), self.dates(1, 3))
        self.assertNotContains(response, '<span class="roomno">№ 101</span>')
        response = self.client.get(reverse('room_list'), {'arrival': 'invalid', 'max_price': '-1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0 найдено')
        self.assertEqual(self.client.get(reverse('room_list'), {'page': 'nonsense'}).status_code, 200)

    def test_csrf_for_mutations(self):
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.user)
        self.assertEqual(c.post(reverse('booking_create', args=[self.room.pk]), self.dates()).status_code, 403)


class ConcurrentBookingTests(TransactionTestCase):
    def test_two_clients_cannot_reserve_same_room(self):
        hotel = Hotel.objects.create(name='Тест', owner='Тест', city='Тест', address='Тест', description='Тест')
        room = Room.objects.create(hotel=hotel, number='1', room_type='single', price=1000, capacity=1, amenities='Душ')
        users = [User.objects.create_user(f'guest{i}', password='test-pass') for i in range(2)]
        clients = [Client(), Client()]
        for c, user in zip(clients, users):
            c.force_login(user)
        barrier = Barrier(2)
        today = timezone.localdate()
        data = {'arrival': str(today), 'departure': str(today+timedelta(days=2)), 'guests': 1}
        def reserve(c):
            close_old_connections()
            try:
                barrier.wait(timeout=5)
                return c.post(reverse('booking_create', args=[room.pk]), data).status_code
            finally:
                close_old_connections()
        with ThreadPoolExecutor(2) as pool:
            statuses = list(pool.map(reserve, clients))
        self.assertCountEqual(statuses, [200, 302])
        self.assertEqual(Booking.objects.count(), 1)
