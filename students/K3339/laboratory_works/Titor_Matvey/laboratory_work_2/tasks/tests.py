from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StudentProfile, Task, Work


def make_task(n=1, discipline='Информатика'):
    return Task.objects.create(
        discipline=discipline,
        teacher_name=f'Учитель {n}',
        issued_on=date.today() - timedelta(days=3),
        due_on=date.today() + timedelta(days=4),
        body=f'Задание номер {n}',
    )


class ListPageTests(TestCase):
    def test_open(self):
        make_task()
        r = self.client.get(reverse('tasks:list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Задание номер 1')

    def test_filter(self):
        make_task(1, 'Физика')
        make_task(2, 'Химия')
        r = self.client.get(reverse('tasks:list'), {'discipline': 'Физика'})
        self.assertContains(r, 'Задание номер 1')
        self.assertNotContains(r, 'Задание номер 2')

    def test_search(self):
        make_task()
        r = self.client.get(reverse('tasks:list'), {'find': 'номер 1'})
        self.assertContains(r, 'Задание номер 1')

    def test_paging(self):
        for i in range(10):
            make_task(i)
        r = self.client.get(reverse('tasks:list'), {'page': 2})
        self.assertEqual(r.status_code, 200)


class DetailPageTests(TestCase):
    def setUp(self):
        self.task = make_task()
        self.student = User.objects.create_user('bob', password='bobpass123')

    def test_404(self):
        r = self.client.get(reverse('tasks:task', args=[999]))
        self.assertEqual(r.status_code, 404)

    def test_send_work(self):
        self.client.login(username='bob', password='bobpass123')
        r = self.client.post(reverse('tasks:task', args=[self.task.pk]), {'button': 'send', 'body': 'мое решение'})
        self.assertEqual(Work.objects.count(), 1)
        self.assertTrue(Work.objects.first().sent_at)

    def test_second_send_blocked(self):
        Work.objects.create(task=self.task, student=self.student, body='уже сдал')
        self.client.login(username='bob', password='bobpass123')
        self.client.post(reverse('tasks:task', args=[self.task.pk]), {'button': 'send', 'body': 'ещё раз'})
        self.assertEqual(Work.objects.count(), 1)

    def test_resend(self):
        Work.objects.create(task=self.task, student=self.student, body='черновик')
        self.client.login(username='bob', password='bobpass123')
        self.client.post(reverse('tasks:task', args=[self.task.pk]), {'button': 'resend', 'body': 'финальная версия'})
        self.assertEqual(Work.objects.get().body, 'финальная версия')

    def test_drop(self):
        Work.objects.create(task=self.task, student=self.student, body='удали меня')
        self.client.login(username='bob', password='bobpass123')
        self.client.post(reverse('tasks:task', args=[self.task.pk]), {'button': 'drop'})
        self.assertEqual(Work.objects.count(), 0)

    def test_scored_work_frozen(self):
        Work.objects.create(task=self.task, student=self.student, body='с отметкой', score=5)
        self.client.login(username='bob', password='bobpass123')
        self.client.post(reverse('tasks:task', args=[self.task.pk]), {'button': 'resend', 'body': 'правка'})
        self.assertEqual(Work.objects.get().body, 'с отметкой')

    def test_teacher_sees_all(self):
        Work.objects.create(task=self.task, student=self.student, body='решение')
        teacher = User.objects.create_user('dir', password='dirpass123', is_staff=True)
        self.client.login(username='dir', password='dirpass123')
        r = self.client.get(reverse('tasks:task', args=[self.task.pk]))
        self.assertContains(r, 'решение')


class SignupTests(TestCase):
    def test_signup_creates_user_and_group(self):
        r = self.client.post(reverse('tasks:signup'), {
            'username': 'newbie',
            'study_group': 'K3339',
            'password1': 'hard-pass-777',
            'password2': 'hard-pass-777',
        })
        self.assertRedirects(r, reverse('login'))
        self.assertTrue(User.objects.filter(username='newbie').exists())
        self.assertEqual(StudentProfile.objects.get(user__username='newbie').study_group, 'K3339')


class MinePageTests(TestCase):
    def test_login_required(self):
        r = self.client.get(reverse('tasks:mine'))
        self.assertEqual(r.status_code, 302)

    def test_only_own(self):
        task = make_task()
        me = User.objects.create_user('ann', password='annpass123')
        other = User.objects.create_user('sid', password='sidpass123')
        Work.objects.create(task=task, student=me, body='моя')
        Work.objects.create(task=task, student=other, body='чужая')
        self.client.login(username='ann', password='annpass123')
        r = self.client.get(reverse('tasks:mine'))
        self.assertContains(r, 'моя')
        self.assertNotContains(r, 'чужая')


class StatsPageTests(TestCase):
    def test_average(self):
        task = make_task()
        u1 = User.objects.create_user('a1', password='pass12345')
        u2 = User.objects.create_user('a2', password='pass12345')
        StudentProfile.objects.create(user=u1, study_group='K3339')
        StudentProfile.objects.create(user=u2, study_group='K3339')
        Work.objects.create(task=task, student=u1, body='1', score=5)
        Work.objects.create(task=task, student=u2, body='2', score=3)
        self.client.login(username='a1', password='pass12345')
        r = self.client.get(reverse('tasks:stats'))
        self.assertContains(r, '4,0')

    def test_staff_sees_groups(self):
        teacher = User.objects.create_user('head', password='headpass123', is_staff=True)
        self.client.login(username='head', password='headpass123')
        r = self.client.get(reverse('tasks:stats'))
        self.assertContains(r, 'по группам')
