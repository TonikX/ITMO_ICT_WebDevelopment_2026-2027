from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Conference, Review, TalkRegistration, Topic


class ConferenceSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.web = Topic.objects.create(name='Веб-технологии')
        cls.ai = Topic.objects.create(name='Искусственный интеллект')
        cls.early = Conference.objects.create(
            title='Неделя науки ИТМО',
            venue_name='Кронверкский проспект, 49',
            venue_description='Главный корпус.',
            start_date=date(2026, 4, 14),
            end_date=date(2026, 4, 16),
            description='Встреча лабораторий.',
            participation_terms='Тезисы до 4 страниц.',
        )
        cls.early.topics.add(cls.web)
        cls.late = Conference.objects.create(
            title='Квантовые вычисления',
            venue_name='Биржевая линия, 16',
            venue_description='Лабораторный корпус.',
            start_date=date(2026, 11, 18),
            end_date=date(2026, 11, 19),
            description='Алгоритмы для семинара.',
            participation_terms='Доклад 12 минут.',
        )
        cls.late.topics.add(cls.ai)
        for index in range(3):
            Conference.objects.create(
                title=f'Семинар {index}',
                venue_name='Аудитория',
                venue_description='Обычная аудитория.',
                start_date=date(2026, 6, 1 + index),
                end_date=date(2026, 6, 2 + index),
                description='Дополнительная конференция для второй страницы.',
                participation_terms='Регистрация открыта.',
            )
        cls.anna = User.objects.create_user(
            'anna', 'anna@example.com', 'guest12345', first_name='Анна', last_name='Ковалёва'
        )
        cls.petr = User.objects.create_user(
            'petr', 'petr@example.com', 'guest12345', first_name='Пётр', last_name='Орлов'
        )
        cls.admin = User.objects.create_user(
            'admin', 'admin@example.com', 'admin12345', is_staff=True, is_superuser=True
        )
        cls.foreign = TalkRegistration.objects.create(
            user=cls.petr,
            conference=cls.early,
            talk_title='Чужой доклад',
            abstract='Пётр уже зарегистрирован.',
        )

    def test_list_is_paginated_and_searchable(self):
        response = self.client.get(reverse('conference_list'))
        self.assertContains(response, 'Неделя науки ИТМО')
        self.assertNotContains(response, 'Квантовые вычисления')
        page_two = self.client.get(reverse('conference_list'), {'page': 2})
        self.assertContains(page_two, 'Квантовые вычисления')
        self.assertContains(page_two, 'page=1')
        found = self.client.get(reverse('conference_list'), {'q': 'Квантовые'})
        self.assertContains(found, 'Квантовые вычисления')
        self.assertNotContains(found, 'Неделя науки')
        by_topic = self.client.get(reverse('conference_list'), {'topic': self.web.pk})
        self.assertContains(by_topic, 'Неделя науки ИТМО')
        self.assertNotContains(by_topic, 'Квантовые вычисления')
        self.assertEqual(self.client.get(reverse('conference_list'), {'topic': 'abc'}).status_code, 200)

    def test_user_registers_and_manages_own_talk(self):
        response = self.client.post(reverse('register'), {
            'username': 'newauthor',
            'first_name': 'Игорь',
            'last_name': 'Смирнов',
            'email': 'igor@example.com',
            'password1': 'Night-river-42',
            'password2': 'Night-river-42',
        })
        self.assertRedirects(response, reverse('conference_list'))
        created = self.client.post(reverse('talk_create', args=[self.early.pk]), {
            'talk_title': 'Свой доклад',
            'abstract': 'Короткий текст.',
        })
        talk = TalkRegistration.objects.get(talk_title='Свой доклад')
        self.assertRedirects(created, reverse('my_talks'))
        self.assertEqual(talk.user.username, 'newauthor')
        edited = self.client.post(reverse('talk_edit', args=[talk.pk]), {
            'talk_title': 'Свой доклад, версия 2',
            'abstract': 'Уточнённый текст.',
        })
        self.assertRedirects(edited, reverse('my_talks'))
        talk.refresh_from_db()
        self.assertEqual(talk.talk_title, 'Свой доклад, версия 2')
        forbidden = self.client.post(reverse('talk_delete', args=[self.foreign.pk]))
        self.assertEqual(forbidden.status_code, 404)
        self.assertTrue(TalkRegistration.objects.filter(pk=self.foreign.pk).exists())
        deleted = self.client.post(reverse('talk_delete', args=[talk.pk]))
        self.assertRedirects(deleted, reverse('my_talks'))
        self.assertFalse(TalkRegistration.objects.filter(pk=talk.pk).exists())

    def test_review_stores_conference_dates_rating_and_author(self):
        self.client.force_login(self.anna)
        response = self.client.post(reverse('review_create', args=[self.early.pk]), {
            'rating': 8,
            'text': 'Понятные условия участия.',
        })
        self.assertRedirects(response, reverse('conference_detail', args=[self.early.pk]))
        review = Review.objects.get(author=self.anna)
        self.assertEqual(review.conference_start, date(2026, 4, 14))
        self.assertEqual(review.conference_end, date(2026, 4, 16))
        self.assertEqual(review.rating, 8)
        page = self.client.get(reverse('conference_detail', args=[self.early.pk]))
        self.assertContains(page, 'Анна Ковалёва')
        self.assertContains(page, '14.04.2026')

    def test_participants_table_filters_by_conference(self):
        TalkRegistration.objects.create(
            user=self.anna, conference=self.late, talk_title='Кубиты', abstract='Обзор.'
        )
        page = self.client.get(reverse('participants'), {'conference': self.early.pk})
        self.assertContains(page, 'Чужой доклад')
        self.assertContains(page, 'Пётр Орлов')
        self.assertNotContains(page, 'Кубиты')
        self.assertNotContains(page, 'Рекомендовать')
        self.assertEqual(self.client.get(reverse('participants'), {'conference': 'abc'}).status_code, 200)

    def test_staff_sets_publication_result_in_the_client(self):
        self.client.force_login(self.admin)
        page = self.client.get(reverse('participants'))
        self.assertContains(page, 'Рекомендовать')
        self.client.logout()
        self.client.force_login(self.anna)
        denied = self.client.post(reverse('set_publication', args=[self.foreign.pk]), {'decision': 'yes'})
        self.assertEqual(denied.status_code, 403)
        self.foreign.refresh_from_db()
        self.assertIsNone(self.foreign.recommended_for_publication)
        self.client.logout()
        self.client.force_login(self.admin)
        saved = self.client.post(
            reverse('set_publication', args=[self.foreign.pk]),
            {'decision': 'yes', 'next': reverse('participants')},
        )
        self.assertRedirects(saved, reverse('participants'))
        self.foreign.refresh_from_db()
        self.assertTrue(self.foreign.recommended_for_publication)
