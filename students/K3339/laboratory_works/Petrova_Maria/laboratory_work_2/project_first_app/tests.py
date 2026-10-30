from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.template import loader
from django.template.backends.jinja2 import Jinja2
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Amenity, Hotel, Reservation, Review, Room, RoomType, Stay


class HotelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('guest', password='Hotel-test-2026!')
        cls.staff = get_user_model().objects.create_superuser(
            'staff', 'staff@example.com', 'Hotel-test-2026!'
        )
        cls.hotel = Hotel.objects.create(name='Hotel & Spa', owner_name='Owner', address='Street')
        cls.room_type = RoomType.objects.create(name='Standard')
        for number in range(1, 8):
            Room.objects.create(
                hotel=cls.hotel, room_type=cls.room_type, number=str(number),
                price=100, capacity=2,
            )
        cls.room = Room.objects.first()
        cls.room.amenities.add(Amenity.objects.create(name='Wi-Fi'))
        cls.today = timezone.localdate()
        cls.reservation = Reservation.objects.create(
            user=cls.user, room=cls.room, check_in=cls.today - timedelta(days=1),
            check_out=cls.today + timedelta(days=1),
        )

    def test_jinja_templates_and_public_pages(self):
        for name in [
            'project_first_app/base.html', 'project_first_app/room_list.html',
            'project_first_app/room_detail.html', 'project_first_app/register.html',
            'project_first_app/my_reservations.html', 'project_first_app/reservation_form.html',
            'project_first_app/reservation_confirm_delete.html',
            'project_first_app/review_form.html', 'project_first_app/recent_guests.html',
            'registration/login.html', 'registration/logged_out.html',
        ]:
            self.assertIsInstance(loader.get_template(name).backend, Jinja2)
        for url in ['/', '/register/', '/accounts/login/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Hotel Service')
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertContains(response, 'Wi-Fi')
        self.assertContains(response, 'Отзывов пока нет')
        self.assertContains(response, 'Hotel &amp; Spa')
        self.assertNotContains(response, '<bound method')
        self.assertIn('Вы вышли', loader.get_template('registration/logged_out.html').render(
            {}, self.client.get('/').wsgi_request
        ))

    def test_filters_and_pagination(self):
        response = self.client.get('/', {
            'search': 'Hotel & Spa', 'room_type': self.room_type.pk,
            'min_capacity': 2, 'max_price': 100,
        })
        self.assertContains(response, 'page=2')
        self.assertContains(response, 'Hotel%20%26%20Spa')
        self.assertContains(response, 'selected')
        self.assertNotContains(response, 'page=0')
        response = self.client.get('/', {'page': 2})
        self.assertContains(response, 'Номер 7')
        self.assertNotContains(response, 'page=3')
        self.assertContains(self.client.get('/', {'max_price': 50}), 'номеров не найдено')

    def test_registration_login_logout_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/register/')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, '<input')
        self.assertNotContains(response, '&lt;input')
        self.assertEqual(client.post('/register/', {}).status_code, 403)
        response = client.post('/register/', {
            'username': 'newguest', 'password1': 'New-hotel-user-2026!',
            'password2': 'New-hotel-user-2026!',
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, reverse('login'))
        response = client.post(reverse('login'), {
            'username': 'newguest', 'password': 'New-hotel-user-2026!',
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, '/')
        self.assertContains(client.get('/'), 'Мои бронирования')
        self.assertEqual(client.get(reverse('logout')).status_code, 405)
        response = client.post(reverse('logout'), {
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, '/')
        self.assertNotContains(client.get('/'), 'Мои бронирования')

    def test_reservation_and_review_pages(self):
        self.client.force_login(self.user)
        for name, args in [
            ('create_reservation', [self.room.pk]), ('my_reservations', []),
            ('edit_reservation', [self.reservation.pk]),
            ('delete_reservation', [self.reservation.pk]),
            ('create_review', [self.room.pk]),
        ]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)
        data = {'check_in': str(self.today + timedelta(days=1)),
                'check_out': str(self.today + timedelta(days=3))}
        self.assertRedirects(
            self.client.post(reverse('create_reservation', args=[self.room.pk]), data),
            reverse('my_reservations'),
        )
        self.assertRedirects(
            self.client.post(reverse('edit_reservation', args=[self.reservation.pk]),
                             {'check_in': str(self.today),
                              'check_out': str(self.today + timedelta(days=1))}),
            reverse('my_reservations'),
        )
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.check_in, self.today)
        self.assertRedirects(self.client.post(reverse('create_review', args=[self.room.pk]), {
            'stay_from': str(self.today), 'stay_to': str(self.today + timedelta(days=1)),
            'text': '<script>test</script>', 'rating': 8,
        }), reverse('room_detail', args=[self.room.pk]))
        self.assertEqual(Review.objects.count(), 1)
        self.assertContains(self.client.get(reverse('room_detail', args=[self.room.pk])),
                            '&lt;script&gt;test&lt;/script&gt;')
        self.assertRedirects(
            self.client.post(reverse('delete_reservation', args=[self.reservation.pk])),
            reverse('my_reservations'),
        )
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    def test_guests_and_navbar(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get('/guests/'), '/')
        self.assertNotContains(self.client.get('/'), 'Постояльцы')
        self.client.force_login(self.staff)
        self.assertContains(self.client.get('/'), 'Постояльцы')
        self.assertContains(self.client.get('/guests/'), 'постояльцев нет')
        Stay.objects.create(user=self.user, room=self.room, check_in=timezone.now())
        self.assertContains(self.client.get('/guests/'), 'Проживает')

    def test_admin_check_in_and_check_out(self):
        self.client.force_login(self.staff)
        reservation_url = reverse('admin:project_first_app_reservation_changelist')
        stay_url = reverse('admin:project_first_app_stay_changelist')
        data = {'action': 'check_in_guests', '_selected_action': [self.reservation.pk]}
        response = self.client.post(reservation_url, data, follow=True)
        self.assertContains(response, 'Заселено: 1')
        stay = Stay.objects.get()
        self.assertEqual(stay.user, self.user)
        self.assertEqual(stay.room, self.room)
        self.assertEqual(timezone.localtime(stay.check_in).date(), self.reservation.check_in)
        self.client.post(reservation_url, data)
        self.assertEqual(Stay.objects.count(), 1)
        self.assertContains(self.client.get(stay_url), 'Проживает')
        checkout = {'action': 'check_out_guests', '_selected_action': [stay.pk]}
        self.assertContains(self.client.post(stay_url, checkout, follow=True), 'Выселено: 1')
        stay.refresh_from_db()
        first_checkout = stay.check_out
        self.assertIsNotNone(first_checkout)
        self.client.post(stay_url, checkout)
        stay.refresh_from_db()
        self.assertEqual(stay.check_out, first_checkout)
        self.assertContains(self.client.get(stay_url), 'Завершено')
        self.client.post(reservation_url, data)
        self.assertEqual(Stay.objects.count(), 1)

    def test_existing_active_stay_is_not_duplicated(self):
        Stay.objects.create(user=self.user, room=self.room, check_in=timezone.now())
        self.client.force_login(self.staff)
        self.client.post(reverse('admin:project_first_app_reservation_changelist'), {
            'action': 'check_in_guests', '_selected_action': [self.reservation.pk],
        })
        self.assertEqual(Stay.objects.count(), 1)

    def test_invalid_forms_and_owner_access(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('create_reservation', args=[self.room.pk]), {})
        self.assertContains(response, 'errorlist')
        other = Reservation.objects.create(
            user=self.staff, room=self.room, check_in=self.today, check_out=self.today,
        )
        for name in ['edit_reservation', 'delete_reservation']:
            self.assertEqual(self.client.get(reverse(name, args=[other.pk])).status_code, 404)

    def test_booking_dates_and_overlaps(self):
        self.client.force_login(self.user)
        self.reservation.delete()
        url = reverse('create_reservation', args=[self.room.pk])
        data = {'check_in': '2026-10-10', 'check_out': '2026-10-15'}
        self.assertRedirects(self.client.post(url, data), reverse('my_reservations'))
        reservation = Reservation.objects.get()
        self.client.force_login(self.staff)
        response = self.client.post(url, {'check_in': '2026-10-12', 'check_out': '2026-10-14'})
        self.assertContains(response, 'Номер уже забронирован на выбранные даты')
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertRedirects(self.client.post(url, {
            'check_in': '2026-10-15', 'check_out': '2026-10-18',
        }), reverse('my_reservations'))
        for start, end in [('2026-10-20', '2026-10-15'), ('2026-10-20', '2026-10-20')]:
            self.assertContains(self.client.post(url, {'check_in': start, 'check_out': end}),
                                'Дата выезда должна быть позже даты заезда')
        self.assertEqual(Reservation.objects.count(), 2)
        self.client.force_login(self.user)
        edit_url = reverse('edit_reservation', args=[reservation.pk])
        self.assertRedirects(self.client.post(edit_url, data), reverse('my_reservations'))
        self.assertContains(self.client.post(edit_url, {
            'check_in': '2026-10-14', 'check_out': '2026-10-16',
        }), 'Номер уже забронирован на выбранные даты')
        self.assertContains(self.client.post(edit_url, {
            'check_in': '2026-10-20', 'check_out': '2026-10-15',
        }), 'Дата выезда должна быть позже даты заезда')
        reservation.refresh_from_db()
        self.assertEqual(reservation.check_in, date(2026, 10, 10))
        self.assertEqual(reservation.check_out, date(2026, 10, 15))

    def test_review_period(self):
        self.client.force_login(self.user)
        for end in ['2026-10-09', '2026-10-10']:
            response = self.client.post(reverse('create_review', args=[self.room.pk]), {
                'stay_from': '2026-10-10', 'stay_to': end, 'text': 'Отзыв', 'rating': 8,
            })
            self.assertContains(response, 'Дата окончания проживания должна быть позже даты начала')
        self.assertEqual(Review.objects.count(), 0)

    def test_recent_guests_period_overlap(self):
        now = timezone.now()
        included = []
        for start, end in [(35, 10), (50, None), (30, 30)]:
            included.append(Stay.objects.create(
                user=self.user, room=self.room, check_in=now - timedelta(days=start),
                check_out=now - timedelta(days=end) if end is not None else None,
            ))
        for start, end in [(40, 35), (-1, None)]:
            Stay.objects.create(
                user=self.user, room=self.room, check_in=now - timedelta(days=start),
                check_out=now - timedelta(days=end) if end is not None else None,
            )
        self.client.force_login(self.staff)
        from django.shortcuts import render
        with patch('project_first_app.views.timezone.now', return_value=now), \
                patch('project_first_app.views.render', wraps=render) as mocked_render:
            self.client.get(reverse('recent_guests'))
        self.assertEqual(list(mocked_render.call_args.args[2]['stays']),
                         sorted(included, key=lambda stay: stay.check_in, reverse=True))
