from datetime import timedelta, datetime, time
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from racing.models import Race, Driver, Entry, Heat, Comment


class RacingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('timur', password='SafeRace2026!', first_name='Данилевский Тимур')
        cls.other = User.objects.create_user('other', password='SafeRace2026!')
        cls.staff = User.objects.create_user('staff', password='SafeRace2026!', is_staff=True)
        cls.driver = Driver.objects.create(user=cls.user, full_name='Данилевский Тимур Давидович', team='Test Team',
                                          car='Porsche GT3 · 565 л.с.', bio='Участник спринтов', experience=4, racing_class='PRO')
        cls.other_driver = Driver.objects.create(user=cls.other, full_name='Другой Участник', team='Other Team',
                                                car='BMW M4', bio='Гонщик', experience=2, racing_class='AM')
        cls.start = timezone.localdate() + timedelta(days=7)
        cls.race = Race.objects.create(title='Тестовый кубок', slug='test-race', track='Игора Драйв', location='Ленинградская область',
                                      start_date=cls.start, end_date=cls.start + timedelta(days=1), round_number=1,
                                      length_km='5.183', corners=14, description='Тестовая гонка', status='open')
        cls.entry = Entry.objects.create(race=cls.race, driver=cls.driver, number=27)

    def login(self, user=None):
        self.client.force_login(user or self.user)

    def entry_data(self, number=28):
        return {'full_name': self.driver.full_name, 'team': 'Updated Team', 'car': 'Porsche GT3',
                'bio': 'Новое описание', 'experience': 5, 'racing_class': 'PRO', 'number': number}

    def comment_data(self, **changes):
        data = {'date_from': self.start.isoformat(), 'date_to': (self.start + timedelta(days=1)).isoformat(),
                'kind': 'racing', 'rating': 9, 'text': 'Когда начнутся заезды?'}
        data.update(changes)
        return data

    def heat_data(self, **changes):
        data = {'entry': self.entry.pk, 'attempt': 1, 'started_at': self.start.isoformat() + 'T12:00',
                'duration': '00:01:42.385', 'position': 1, 'status': 'finished', 'note': ''}
        data.update(changes)
        return data

    def test_public_pages_render_with_jinja(self):
        for name, args in [('home', []), ('races', []), ('drivers', []), ('race_detail', [self.race.slug]), ('login', []), ('signup', [])]:
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 200, name)
            self.assertContains(response, 'APEX')
            self.assertNotContains(response, '{%')

    def test_signup_creates_user_and_session(self):
        response = self.client.post(reverse('signup'), {'full_name': 'Новый Гонщик', 'username': 'newracer',
                                                       'password1': 'V7!circuit-Pulse', 'password2': 'V7!circuit-Pulse'})
        self.assertRedirects(response, reverse('races'))
        self.assertEqual(User.objects.get(username='newracer').first_name, 'Новый Гонщик')
        self.assertIn('_auth_user_id', self.client.session)

    def test_weak_password_rejected(self):
        self.client.post(reverse('signup'), {'full_name': 'Гонщик', 'username': 'weak', 'password1': '123', 'password2': '123'})
        self.assertFalse(User.objects.filter(username='weak').exists())

    def test_login_and_post_logout(self):
        response = self.client.post(reverse('login'), {'username': 'timur', 'password': 'SafeRace2026!'})
        self.assertRedirects(response, reverse('my_entries'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_external_login_next_is_ignored(self):
        response = self.client.post(reverse('login'), {'username': 'timur', 'password': 'SafeRace2026!', 'next': 'https://evil.example/'})
        self.assertRedirects(response, reverse('my_entries'))

    def test_anonymous_cannot_write(self):
        for name, args in [('entry_create', [self.race.slug]), ('comment_add', [self.race.slug]), ('heat_create', [self.race.slug])]:
            response = self.client.post(reverse(name, args=args), {})
            self.assertEqual(response.status_code, 302)
            self.assertIn('/account/login/', response.url)
        self.assertEqual(Comment.objects.count(), 0)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse('comment_add', args=[self.race.slug]), self.comment_data()).status_code, 403)

    def test_new_user_can_create_driver_and_entry(self):
        self.login(self.staff)
        response = self.client.post(reverse('entry_create', args=[self.race.slug]), self.entry_data(63))
        self.assertRedirects(response, reverse('my_entries'))
        self.assertTrue(Entry.objects.filter(race=self.race, driver__user=self.staff, number=63).exists())

    def test_owner_edits_registration(self):
        self.login()
        response = self.client.post(reverse('entry_edit', args=[self.race.slug, self.entry.pk]), self.entry_data())
        self.assertRedirects(response, reverse('my_entries'))
        self.entry.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(self.entry.number, 28)
        self.assertEqual(self.driver.team, 'Updated Team')

    def test_foreign_registration_is_inaccessible(self):
        self.login(self.other)
        for name, args in [('entry_edit', [self.race.slug, self.entry.pk]), ('entry_delete', [self.entry.pk])]:
            self.assertEqual(self.client.post(reverse(name, args=args), self.entry_data()).status_code, 404)
        self.assertTrue(Entry.objects.filter(pk=self.entry.pk).exists())

    def test_form_keeps_updated_driver_name(self):
        self.driver.full_name = 'Обновлённое Имя Гонщика'
        self.driver.save()
        self.login()
        response = self.client.get(reverse('entry_edit', args=[self.race.slug, self.entry.pk]))
        self.assertContains(response, 'value="Обновлённое Имя Гонщика"')

    def test_owner_deletes_only_after_post(self):
        self.login()
        target = reverse('entry_delete', args=[self.entry.pk])
        self.assertEqual(self.client.get(target).status_code, 200)
        self.assertTrue(Entry.objects.filter(pk=self.entry.pk).exists())
        self.assertRedirects(self.client.post(target), reverse('my_entries'))
        self.assertFalse(Entry.objects.filter(pk=self.entry.pk).exists())

    def test_duplicate_number_rejected(self):
        self.login(self.other)
        response = self.client.post(reverse('entry_create', args=[self.race.slug]), self.entry_data(27))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Этот номер уже занят')
        self.assertEqual(self.race.entries.count(), 1)

    def test_number_limits(self):
        self.login(self.other)
        for number in [0, 1000]:
            self.client.post(reverse('entry_create', args=[self.race.slug]), self.entry_data(number))
        self.assertEqual(self.race.entries.count(), 1)

    def test_duplicate_registration_rejected(self):
        self.login()
        self.assertRedirects(self.client.post(reverse('entry_create', args=[self.race.slug]), self.entry_data()), reverse('my_entries'))
        self.assertEqual(self.race.entries.count(), 1)

    def test_capacity_rejected(self):
        self.race.capacity = 1
        self.race.save()
        self.login(self.other)
        response = self.client.post(reverse('entry_create', args=[self.race.slug]), self.entry_data(99))
        self.assertContains(response, 'Все места заняты')
        self.assertEqual(self.race.entries.count(), 1)

    def test_registration_closed_cannot_modify_or_delete(self):
        self.race.status = 'finished'
        self.race.save()
        self.login()
        self.assertEqual(self.client.post(reverse('entry_edit', args=[self.race.slug, self.entry.pk]), self.entry_data()).status_code, 403)
        self.assertEqual(self.client.post(reverse('entry_delete', args=[self.entry.pk])).status_code, 403)

    def test_registration_with_results_is_locked(self):
        Heat.objects.create(entry=self.entry, attempt=1, started_at=timezone.make_aware(datetime.combine(self.start, time(12))),
                            duration=timedelta(seconds=100), position=1)
        self.login()
        self.assertEqual(self.client.post(reverse('entry_edit', args=[self.race.slug, self.entry.pk]), self.entry_data()).status_code, 403)
        self.assertEqual(self.client.post(reverse('entry_delete', args=[self.entry.pk])).status_code, 403)

    def test_comment_persists_all_variant_fields_and_author(self):
        self.login()
        self.client.post(reverse('comment_add', args=[self.race.slug]), self.comment_data(author=self.other.pk))
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.kind, 'racing')
        self.assertEqual(comment.rating, 9)
        self.assertEqual(comment.date_from, self.start)
        self.assertEqual(comment.date_to, self.race.end_date)

    def test_invalid_comments_rejected(self):
        self.login()
        for changes in [{'rating': 0}, {'rating': 11}, {'kind': 'invalid'}, {'date_to': (self.start-timedelta(days=1)).isoformat()},
                        {'date_from': (self.start-timedelta(days=3)).isoformat()}, {'text': ''}]:
            response = self.client.post(reverse('comment_add', args=[self.race.slug]), self.comment_data(**changes))
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comments_escape_html(self):
        self.login()
        self.client.post(reverse('comment_add', args=[self.race.slug]), self.comment_data(text='<script>alert(1)</script>'))
        response = self.client.get(reverse('race_detail', args=[self.race.slug]))
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_user_has_no_staff_controls_or_access(self):
        self.login()
        self.assertNotContains(self.client.get(reverse('race_detail', args=[self.race.slug])), 'Добавить результат')
        for name, args in [('control', []), ('heat_create', [self.race.slug])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 403)
            self.assertEqual(self.client.post(reverse(name, args=args), self.heat_data()).status_code, 403)
        self.assertEqual(Heat.objects.count(), 0)

    def test_staff_sees_controls_and_creates_result(self):
        self.login(self.staff)
        self.assertContains(self.client.get(reverse('race_detail', args=[self.race.slug])), 'Добавить результат')
        self.assertEqual(self.client.get(reverse('control')).status_code, 200)
        response = self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data())
        self.assertEqual(response.status_code, 302)
        self.assertAlmostEqual(Heat.objects.get().duration.total_seconds(), 102.385)

    def test_staff_updates_result(self):
        self.login(self.staff)
        self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data())
        heat = Heat.objects.get()
        response = self.client.post(reverse('heat_edit', args=[self.race.slug, heat.pk]), self.heat_data(duration='00:01:40.111'))
        self.assertEqual(response.status_code, 302)
        heat.refresh_from_db()
        self.assertAlmostEqual(heat.duration.total_seconds(), 100.111)

    def test_protocol_displays_moscow_time(self):
        Heat.objects.create(entry=self.entry, attempt=1,
                            started_at=timezone.make_aware(datetime.combine(self.start, time(12))),
                            duration=timedelta(seconds=100), position=1)
        response = self.client.get(reverse('race_detail', args=[self.race.slug]))
        self.assertContains(response, self.start.strftime('%d.%m.%Y') + ' 12:00')

    def test_invalid_heat_times_and_dates_rejected(self):
        self.login(self.staff)
        for changes in [{'duration': '-00:01:00'}, {'duration': '00:00:00'}, {'duration': ''}, {'position': ''},
                        {'started_at': (self.start-timedelta(days=1)).isoformat()+'T12:00'}]:
            response = self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data(**changes))
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Heat.objects.count(), 0)

    def test_dnf_without_time_or_position(self):
        self.login(self.staff)
        self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data(status='dnf', duration='', position=''))
        heat = Heat.objects.get()
        self.assertEqual(heat.status, 'dnf')
        self.assertIsNone(heat.duration)
        self.assertIsNone(heat.position)

    def test_duplicate_heat_attempt_or_position_rejected(self):
        self.login(self.staff)
        self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data())
        self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data())
        other_entry = Entry.objects.create(race=self.race, driver=self.other_driver, number=63)
        response = self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data(entry=other_entry.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Heat.objects.count(), 1)

    def test_staff_cannot_use_entry_from_different_race(self):
        second = Race.objects.create(title='Другая гонка', slug='other', track='Другая', location='Казань', start_date=self.start,
                                     end_date=self.start, round_number=2, length_km=3, corners=10, description='Тест')
        foreign = Entry.objects.create(race=second, driver=self.other_driver, number=1)
        self.login(self.staff)
        self.client.post(reverse('heat_create', args=[self.race.slug]), self.heat_data(entry=foreign.pk))
        self.assertEqual(Heat.objects.count(), 0)

    def test_search_filters_and_pagination_preserve_query(self):
        for i in range(8):
            Race.objects.create(title=f'Кубок {i}', slug=f'cup-{i}', track='Казань', location='Казань', start_date=self.start,
                                end_date=self.start, round_number=i+2, length_km=3, corners=10, description='Тест')
        response = self.client.get(reverse('races'), {'q': 'Кубок', 'status': 'open'})
        self.assertEqual(response.content.count(b'class="race-card"'), 6)
        self.assertContains(response, 'q=')
        self.assertContains(response, 'status=open')
        self.assertContains(response, 'page=2')
        self.assertEqual(self.client.get(reverse('races'), {'page': 'invalid'}).status_code, 200)
        self.assertEqual(self.client.get(reverse('races'), {'page': 999}).status_code, 200)
        self.assertEqual(self.client.get(reverse('drivers'), {'class': 'PRO'}).content.count(b'class="driver-card"'), 1)

    def test_database_enforces_duplicate_entries_and_rating(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Entry.objects.create(race=self.race, driver=self.other_driver, number=27)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(race=self.race, author=self.user, date_from=self.start, date_to=self.start, text='Test', kind='other', rating=11)

    def test_admin_can_manage_heat(self):
        self.staff.is_superuser = True
        self.staff.save()
        self.login(self.staff)
        response = self.client.get(reverse('admin:racing_heat_add'))
        self.assertEqual(response.status_code, 200)
        data = self.heat_data()
        data.pop('started_at')
        data.update(started_at_0=self.start.isoformat(), started_at_1='12:00:00')
        response = self.client.post(reverse('admin:racing_heat_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Heat.objects.count(), 1)
