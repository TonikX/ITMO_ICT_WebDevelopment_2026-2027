from datetime import date, datetime, timedelta
import secrets
import re
from html import unescape
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from .models import Homework, StudentProfile, StudyGroup, Subject, Submission
from .forms import GradeForm
from .views import get_submission_status


class GradeJournalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.teacher = User.objects.create_user(username='journal_teacher', is_staff=True)
        cls.other_teacher = User.objects.create_user(username='journal_other_teacher', is_staff=True)
        cls.empty_teacher = User.objects.create_user(username='journal_empty_teacher', is_staff=True)
        cls.admin = User.objects.create_superuser(username='journal_admin', password=None)
        permissions = Permission.objects.filter(
            content_type__app_label='homework',
            codename__in=['view_homework', 'view_submission', 'change_submission'],
        )
        for teacher in [cls.teacher, cls.other_teacher, cls.empty_teacher]:
            teacher.user_permissions.add(*permissions)
        cls.group = StudyGroup.objects.create(group_name='ИС-22')
        cls.other_group = StudyGroup.objects.create(group_name='ИС-23')
        cls.forbidden_group = StudyGroup.objects.create(group_name='ИС-24')
        cls.no_homework_group = StudyGroup.objects.create(group_name='Без заданий')
        cls.student = User.objects.create_user(
            username='journal_maria', first_name='Мария', last_name='Иванова',
            email='private-maria@example.com', password=secrets.token_urlsafe(24),
        )
        cls.classmate = User.objects.create_user(
            username='journal_dmitry', first_name='Дмитрий', last_name='Петров',
            email='private-dmitry@example.com', password=secrets.token_urlsafe(24),
        )
        cls.no_answers_student = User.objects.create_user(
            username='journal_ulyana', first_name='Ульяна', last_name='Ипатова'
        )
        cls.foreign_student = User.objects.create_user(
            username='journal_foreign', first_name='ЧужоеИмя', last_name='ЧужаяФамилия'
        )
        for student in [cls.student, cls.classmate, cls.no_answers_student]:
            StudentProfile.objects.create(user=student, study_group=cls.group)
        StudentProfile.objects.create(user=cls.foreign_student, study_group=cls.other_group)
        cls.math = Subject.objects.create(subject_name='Математика')
        cls.database_subject = Subject.objects.create(subject_name='Базы данных')
        deadline = timezone.localdate() + timedelta(days=7)
        cls.math_one = Homework.objects.create(
            teacher=cls.teacher, study_group=cls.group, subject=cls.math,
            description='Long description not for the column header. ' * 20, deadline=deadline,
        )
        cls.math_two = Homework.objects.create(
            teacher=cls.other_teacher, study_group=cls.group, subject=cls.math,
            description='Second math assignment', deadline=deadline,
        )
        cls.unsubmitted_homework = Homework.objects.create(
            teacher=cls.teacher, study_group=cls.group, subject=cls.database_subject,
            description='Nobody has submitted this homework', deadline=deadline,
        )
        cls.other_group_homework = Homework.objects.create(
            teacher=cls.teacher, study_group=cls.other_group, subject=cls.database_subject,
            description='Another accessible group', deadline=deadline,
        )
        cls.forbidden_homework = Homework.objects.create(
            teacher=cls.other_teacher, study_group=cls.forbidden_group, subject=cls.math,
            description='Inaccessible group homework', deadline=deadline,
        )
        cls.first_submission = Submission.objects.create(
            student=cls.student, homework=cls.math_one, answer_text='PRIVATE_FIRST_ANSWER', grade=5
        )
        cls.second_submission = Submission.objects.create(
            student=cls.classmate, homework=cls.math_one, answer_text='PRIVATE_SECOND_ANSWER', grade=4
        )
        Submission.objects.create(
            student=cls.student, homework=cls.math_two, answer_text='PRIVATE_PENDING_ANSWER'
        )
        cls.other_teacher_submission = Submission.objects.create(
            student=cls.classmate, homework=cls.math_two, answer_text='PRIVATE_OTHER_TEACHER_ANSWER', grade=3
        )

    def setUp(self):
        self.client.force_login(self.student)
        self.url = reverse('homework:grades')

    def table_rows(self, response):
        body = re.search(r'<tbody>(.*?)</tbody>', response.content.decode(), re.S)
        self.assertIsNotNone(body)
        return re.findall(r'<tr[^>]*>(.*?)</tr>', body.group(1), re.S)

    def row_grades(self, row):
        cells = re.findall(r'<td>(.*?)</td>', row, re.S)
        values = []
        for cell in cells:
            values.append(re.sub(r'<[^>]+>', '', cell).strip())
        return values

    def test_student_sees_all_classmates_assignments_and_correct_grades(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Журнал оценок')
        self.assertContains(response, self.group.group_name)
        rows = self.table_rows(response)
        self.assertEqual(len(rows), 3)
        self.assertIn('Иванова Мария', rows[0])
        self.assertIn('Ипатова Ульяна', rows[1])
        self.assertIn('Петров Дмитрий', rows[2])
        self.assertEqual(self.row_grades(rows[0]), ['—', '5', '—'])
        self.assertEqual(self.row_grades(rows[1]), ['—', '—', '—'])
        self.assertEqual(self.row_grades(rows[2]), ['—', '4', '3'])
        self.assertContains(response, 'class="current-user"', count=1)
        self.assertNotContains(response, 'На проверке')
        self.assertNotContains(response, 'name="group"')
        self.assertContains(response, 'Назад к домашним заданиям')
        self.assertContains(response, 'class="journal-scroll"')

    def test_columns_are_individual_homeworks_in_stable_subject_date_id_order(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        ordered = [self.unsubmitted_homework.pk, self.math_one.pk, self.math_two.pk]
        previous_position = -1
        for pk in ordered:
            marker = 'ДЗ №' + str(pk)
            self.assertContains(response, marker)
            position = html.index(marker)
            self.assertGreater(position, previous_position)
            previous_position = position
        self.assertContains(response, self.math_one.deadline.strftime('%d.%m.%Y'))
        self.assertNotContains(response, self.math_one.description)
        self.assertNotContains(response, 'ДЗ №' + str(self.other_group_homework.pk))

    def test_journal_does_not_expose_answers_email_passwords_or_foreign_students(self):
        response = self.client.get(self.url)
        for private_value in [
            self.first_submission.answer_text, self.second_submission.answer_text,
            self.other_teacher_submission.answer_text, 'PRIVATE_PENDING_ANSWER',
            self.student.email, self.classmate.email, self.classmate.password,
            self.foreign_student.last_name,
        ]:
            self.assertNotContains(response, private_value)
        self.assertNotContains(response, reverse('homework:teacher_grade', args=[self.second_submission.pk]))

    def test_student_cannot_select_another_group_or_use_a_post_to_change_grades(self):
        for group in [self.other_group, self.forbidden_group]:
            self.assertEqual(self.client.get(self.url, {'group': group.pk}).status_code, 403)
        self.assertEqual(self.client.get(self.url, {'group': self.group.pk}).status_code, 200)
        response = self.client.post(self.url, {'group': self.group.pk, 'grade': 2, 'submission': self.second_submission.pk})
        self.assertEqual(response.status_code, 405)
        self.second_submission.refresh_from_db()
        self.assertEqual(self.second_submission.grade, 4)

    def test_guest_and_user_without_profile_are_denied(self):
        self.client.logout()
        self.assertRedirects(self.client.get(self.url), reverse('homework:login') + '?next=' + self.url)
        user = get_user_model().objects.create_user(username='journal_no_profile')
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_teacher_selects_only_taught_groups_and_reads_the_whole_group(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.url, {'group': self.group.pk})
        self.assertContains(response, 'name="group"')
        self.assertContains(response, self.group.group_name)
        self.assertContains(response, self.other_group.group_name)
        self.assertNotContains(response, self.forbidden_group.group_name)
        self.assertEqual(self.row_grades(self.table_rows(response)[2]), ['—', '4', '3'])
        own_answers = reverse('homework:teacher_submissions', args=[self.math_one.pk])
        foreign_answers = reverse('homework:teacher_submissions', args=[self.math_two.pk])
        self.assertContains(response, own_answers)
        self.assertNotContains(response, foreign_answers)
        self.assertEqual(self.client.get(foreign_answers).status_code, 404)
        foreign_grade = reverse('homework:teacher_grade', args=[self.other_teacher_submission.pk])
        self.assertEqual(self.client.post(foreign_grade, {'grade': 5}).status_code, 404)
        self.other_teacher_submission.refresh_from_db()
        self.assertEqual(self.other_teacher_submission.grade, 3)
        self.assertEqual(self.client.get(self.url, {'group': self.forbidden_group.pk}).status_code, 404)
        self.assertEqual(self.client.get(self.url, {'group': self.other_group.pk}).status_code, 200)

    def test_teacher_needs_both_read_permissions(self):
        self.client.force_login(self.teacher)
        for codename in ['view_homework', 'view_submission']:
            permission = Permission.objects.get(codename=codename)
            self.teacher.user_permissions.remove(permission)
            self.assertEqual(self.client.get(self.url).status_code, 403)
            self.assertNotContains(self.client.get(reverse('homework:teacher')), 'Журнал оценок')
            self.teacher.user_permissions.add(permission)

    def test_superuser_can_read_all_groups(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url, {'group': self.group.pk})
        self.assertEqual(len(self.table_rows(response)), 3)
        for group in [self.group, self.other_group, self.forbidden_group, self.no_homework_group]:
            self.assertContains(response, group.group_name)
            self.assertEqual(self.client.get(self.url, {'group': group.pk}).status_code, 200)
        self.assertContains(response, 'Назад в Django Admin')

    def test_empty_teacher_and_missing_or_invalid_group(self):
        self.client.force_login(self.empty_teacher)
        self.assertContains(self.client.get(self.url), 'У вас пока нет учебных групп с назначенными заданиями')
        self.assertContains(self.client.get(reverse('homework:teacher')), 'У вас пока нет учебных групп с назначенными заданиями')
        self.client.force_login(self.teacher)
        for group in ['invalid', '999999', '9' * 100, '-1']:
            self.assertEqual(self.client.get(self.url, {'group': group}).status_code, 404)

    def test_groups_without_students_or_homework_have_clear_messages(self):
        profile = self.student.student_profile
        profile.study_group = self.no_homework_group
        profile.save()
        self.assertContains(self.client.get(self.url), 'Для этой группы пока нет домашних заданий')
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(self.url, {'group': self.other_group.pk}), 'Оценки учеников группы')
        empty_group = StudyGroup.objects.create(group_name='Нет учеников')
        Homework.objects.create(
            teacher=self.teacher, study_group=empty_group, subject=self.math,
            description='Empty group homework', deadline=timezone.localdate() + timedelta(days=1),
        )
        response = self.client.get(self.url, {'group': empty_group.pk})
        self.assertContains(response, 'В этой группе пока нет учеников')

    def test_table_remains_when_all_grades_are_null(self):
        Submission.objects.filter(homework__study_group=self.group).update(grade=None)
        response = self.client.get(self.url)
        rows = self.table_rows(response)
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(self.row_grades(row), ['—', '—', '—'])

    def test_student_sorting_uses_user_id_when_names_match(self):
        for patronymic, grade in [('А', 2), ('Б', 3)]:
            student = get_user_model().objects.create_user(
                username='same_name_' + str(grade), last_name='Иванова', first_name='Мария'
            )
            StudentProfile.objects.create(user=student, study_group=self.group, patronymic=patronymic)
            Submission.objects.create(student=student, homework=self.unsubmitted_homework, answer_text='Answer', grade=grade)
        rows = self.table_rows(self.client.get(self.url))
        self.assertIn('Иванова Мария А', rows[1])
        self.assertIn('Иванова Мария Б', rows[2])
        self.assertEqual(self.row_grades(rows[1])[0], '2')
        self.assertEqual(self.row_grades(rows[2])[0], '3')

    def test_staff_profiles_are_not_listed_as_students_and_name_fallback_works(self):
        StudentProfile.objects.create(user=self.teacher, study_group=self.group)
        response = self.client.get(self.url)
        self.assertEqual(len(self.table_rows(response)), 3)
        student = get_user_model().objects.create_user(username='journal_name_fallback')
        StudentProfile.objects.create(user=student, study_group=self.group)
        self.assertContains(self.client.get(self.url), student.username)

    def test_grades_update_after_existing_teacher_page_and_admin_save(self):
        self.client.force_login(self.teacher)
        url = reverse('homework:teacher_grade', args=[self.second_submission.pk])
        self.assertEqual(self.client.post(url, {'grade': 5}).status_code, 302)
        response = self.client.get(self.url, {'group': self.group.pk})
        self.assertEqual(self.row_grades(self.table_rows(response)[2]), ['—', '5', '3'])
        admin_url = reverse('admin:homework_submission_change', args=[self.second_submission.pk])
        self.assertEqual(self.client.post(admin_url, {'grade': 4, '_save': 'Save'}).status_code, 302)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(self.row_grades(self.table_rows(response)[2]), ['—', '4', '3'])

    def test_navigation_links_and_group_selector_on_dashboard(self):
        response = self.client.get(reverse('homework:homeworks'))
        self.assertContains(response, 'Журнал оценок группы')
        self.assertContains(response, self.url)
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('homework:teacher'))
        self.assertContains(response, 'Журнал оценок')
        self.assertContains(response, 'name="group"')
        self.assertContains(response, self.group.group_name)
        self.assertContains(response, self.other_group.group_name)
        self.assertNotContains(response, self.forbidden_group.group_name)

    def test_dashboard_group_filter_and_return_to_all_assignments(self):
        self.client.force_login(self.teacher)
        dashboard_url = reverse('homework:teacher')
        response = self.client.get(dashboard_url)
        self.assertContains(response, '<option value="" selected>Все домашние задания</option>', html=True)
        self.assertContains(response, 'class="homework-card"', count=3)
        self.assertContains(response, '<select', count=3)
        self.assertContains(response, 'onchange="this.form.submit()"')
        self.assertContains(response, 'action="' + dashboard_url + '"')
        self.assertNotContains(response, 'Применить фильтр')
        for group, count, absent_homework in [
            (self.group, 2, self.other_group_homework),
            (self.other_group, 1, self.math_one),
        ]:
            response = self.client.get(dashboard_url, {'group': group.pk, 'teacher': self.other_teacher.pk})
            self.assertContains(response, 'class="homework-card"', count=count)
            self.assertContains(response, '<option value="' + str(group.pk) + '" selected>')
            self.assertNotContains(response, reverse('homework:teacher_submissions', args=[absent_homework.pk]))
            self.assertNotContains(response, reverse('homework:teacher_submissions', args=[self.math_two.pk]))
            self.assertContains(response, self.url + '?group=' + str(group.pk))
        response = self.client.get(dashboard_url, {'group': ''})
        self.assertContains(response, 'class="homework-card"', count=3)
        self.assertContains(response, 'href="' + self.url + '">Открыть журнал оценок</a>')

    def test_dashboard_rejects_invalid_or_inaccessible_groups(self):
        self.client.force_login(self.teacher)
        dashboard_url = reverse('homework:teacher')
        for group in ['invalid', '999999', '-1', '9' * 100, str(self.forbidden_group.pk)]:
            self.assertEqual(self.client.get(dashboard_url, {'group': group}).status_code, 404)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(dashboard_url, {'group': self.group.pk}).status_code, 403)

    def test_homework_filter_does_not_require_journal_permission(self):
        self.teacher.user_permissions.remove(Permission.objects.get(codename='view_submission'))
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('homework:teacher'), {'group': self.group.pk})
        self.assertContains(response, 'class="homework-card"', count=2)
        self.assertContains(response, 'name="group"')
        self.assertNotContains(response, 'Открыть журнал оценок')

    def test_journal_group_switch_keeps_selection_and_has_no_submit_button(self):
        Submission.objects.create(
            student=self.foreign_student, homework=self.other_group_homework,
            answer_text='PRIVATE_GROUP_SWITCH_ANSWER', grade=2,
        )
        self.client.force_login(self.teacher)
        for group, expected_rows in [(self.group, 3), (self.other_group, 1), (self.group, 3)]:
            response = self.client.get(self.url, {'group': group.pk})
            self.assertEqual(len(self.table_rows(response)), expected_rows)
            self.assertContains(response, '<option value="' + str(group.pk) + '" selected>')
            self.assertContains(response, 'onchange="this.form.submit()"')
            self.assertNotContains(response, 'Открыть журнал')
            self.assertNotContains(response, 'Все домашние задания')
            self.assertNotContains(response, 'PRIVATE_GROUP_SWITCH_ANSWER')
            if group == self.other_group:
                rows = self.table_rows(response)
                self.assertIn(self.foreign_student.last_name, rows[0])
                self.assertEqual(self.row_grades(rows[0]), ['2'])
                self.assertNotContains(response, self.student.last_name)
        self.client.force_login(self.admin)
        response = self.client.get(self.url, {'group': self.other_group.pk})
        self.assertContains(response, 'onchange="this.form.submit()"')
        self.assertEqual(self.row_grades(self.table_rows(response)[0]), ['2'])

    def test_number_of_queries_does_not_grow_for_each_cell(self):
        with CaptureQueriesContext(connection) as small:
            self.assertEqual(self.client.get(self.url).status_code, 200)
        for number in range(6):
            user = get_user_model().objects.create_user(username='journal_extra_' + str(number))
            StudentProfile.objects.create(user=user, study_group=self.group)
            Homework.objects.create(
                teacher=self.teacher, study_group=self.group, subject=self.math,
                description='Extra homework ' + str(number),
                deadline=timezone.localdate() + timedelta(days=2),
            )
        with CaptureQueriesContext(connection) as large:
            self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(len(small), len(large))


class TeacherWorkspaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.password = secrets.token_urlsafe(24)
        cls.teacher = User.objects.create_user(
            username='teacher_one', first_name='Елена', is_staff=True, password=cls.password
        )
        cls.other_teacher = User.objects.create_user(username='teacher_two', is_staff=True)
        cls.admin = User.objects.create_superuser(username='workspace_admin', password=None)
        cls.student = User.objects.create_user(username='workspace_student', first_name='Ульяна', last_name='Иванова')
        cls.other_student = User.objects.create_user(username='workspace_other_student')
        cls.group = StudyGroup.objects.create(group_name='ИС-22')
        cls.other_group = StudyGroup.objects.create(group_name='ИС-23')
        StudentProfile.objects.create(user=cls.student, study_group=cls.group)
        StudentProfile.objects.create(user=cls.other_student, study_group=cls.other_group)
        cls.subject = Subject.objects.create(subject_name='Математика')
        cls.other_subject = Subject.objects.create(subject_name='Программирование')
        permissions = Permission.objects.filter(
            content_type__app_label='homework',
            codename__in=[
                'view_homework', 'add_homework', 'change_homework',
                'view_submission', 'change_submission',
                'view_subject', 'view_studygroup', 'view_studentprofile',
            ],
        )
        cls.teacher.user_permissions.add(*permissions)
        cls.other_teacher.user_permissions.add(*permissions)
        cls.homework = Homework.objects.create(
            teacher=cls.teacher, subject=cls.subject, study_group=cls.group,
            description='Own assignment with an answer',
            deadline=timezone.localdate() + timedelta(days=7),
        )
        cls.empty_homework = Homework.objects.create(
            teacher=cls.teacher, subject=cls.other_subject, study_group=cls.other_group,
            description='Own assignment without answers',
            deadline=timezone.localdate() + timedelta(days=5),
        )
        cls.foreign_homework = Homework.objects.create(
            teacher=cls.other_teacher, subject=cls.subject, study_group=cls.group,
            description='Other teacher private assignment',
            deadline=timezone.localdate() + timedelta(days=7),
        )
        cls.submission = Submission.objects.create(
            student=cls.student, homework=cls.homework, answer_text='Private pupil answer'
        )
        cls.foreign_submission = Submission.objects.create(
            student=cls.student, homework=cls.foreign_homework,
            answer_text='Other teacher pupil answer', grade=4,
        )

    def setUp(self):
        self.client.force_login(self.teacher)
        self.create_url = reverse('homework:teacher_homework_create')
        self.edit_url = reverse('homework:teacher_homework_edit', args=[self.homework.pk])
        self.answers_url = reverse('homework:teacher_submissions', args=[self.homework.pk])
        self.grade_url = reverse('homework:teacher_grade', args=[self.submission.pk])

    def homework_data(self):
        return {
            'subject': self.subject.pk, 'study_group': self.group.pk,
            'issue_at': timezone.localdate().isoformat(),
            'deadline': (timezone.localdate() + timedelta(days=7)).isoformat(),
            'description': 'New teacher assignment', 'penalty_info': 'Late work penalty',
        }

    def test_login_opens_own_dashboard(self):
        self.client.logout()
        response = self.client.post(reverse('homework:login'), {
            'username': self.teacher.username, 'password': self.password,
        }, follow=True)
        self.assertEqual(response.redirect_chain[-1][0], reverse('homework:teacher'))
        self.assertContains(response, 'Кабинет преподавателя')
        self.assertContains(response, self.teacher.first_name)
        self.assertContains(response, self.homework.description)
        self.assertContains(response, self.empty_homework.description)
        self.assertContains(response, 'Отправили ответы: 1')
        self.assertContains(response, 'Создать домашнее задание')
        self.assertNotContains(response, self.foreign_homework.description)

    def test_empty_dashboard_and_empty_answers(self):
        new_teacher = get_user_model().objects.create_user(username='empty_teacher', is_staff=True)
        new_teacher.user_permissions.add(Permission.objects.get(codename='view_homework'))
        self.client.force_login(new_teacher)
        self.assertContains(self.client.get(reverse('homework:teacher')), 'У вас пока нет домашних заданий')
        self.client.force_login(self.teacher)
        url = reverse('homework:teacher_submissions', args=[self.empty_homework.pk])
        self.assertContains(self.client.get(url), 'Ученики пока не отправили ответы на это задание')

    def test_filtered_homework_cards_keep_edit_and_answer_links(self):
        response = self.client.get(reverse('homework:teacher'), {'group': self.group.pk})
        self.assertContains(response, self.edit_url)
        self.assertContains(response, self.answers_url)
        self.assertContains(response, 'class="homework-card"', count=1)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        self.assertEqual(self.client.get(self.answers_url).status_code, 200)

    def test_create_uses_current_teacher_and_reaches_only_correct_group(self):
        response = self.client.get(self.create_url)
        self.assertContains(response, '<select', count=2)
        self.assertNotContains(response, 'name="teacher"')
        data = self.homework_data()
        data['teacher'] = self.other_teacher.pk
        response = self.client.post(self.create_url, data)
        self.assertRedirects(response, reverse('homework:teacher'))
        homework = Homework.objects.get(description=data['description'])
        self.assertEqual(homework.teacher, self.teacher)
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('homework:homeworks')), data['description'])
        self.client.force_login(self.other_student)
        self.assertNotContains(self.client.get(reverse('homework:homeworks')), data['description'])

    def test_create_checks_required_fields_dates_and_existing_choices(self):
        count = Homework.objects.count()
        for changes in [
            {'description': ''}, {'subject': '999999'}, {'study_group': 'New group'},
            {'deadline': (timezone.localdate() - timedelta(days=1)).isoformat()},
        ]:
            data = self.homework_data()
            data.update(changes)
            response = self.client.post(self.create_url, data)
            self.assertContains(response, 'class="errorlist')
            self.assertEqual(Homework.objects.count(), count)

    def test_edit_all_fields_before_first_submission(self):
        data = self.homework_data()
        data.update({'description': 'Edited before submission', 'teacher': self.other_teacher.pk})
        url = reverse('homework:teacher_homework_edit', args=[self.empty_homework.pk])
        self.assertRedirects(self.client.post(url, data), reverse('homework:teacher'))
        self.empty_homework.refresh_from_db()
        self.assertEqual(self.empty_homework.study_group, self.group)
        self.assertEqual(self.empty_homework.subject, self.subject)
        self.assertEqual(self.empty_homework.teacher, self.teacher)

    def test_edit_locks_group_subject_and_dates_after_submission(self):
        data = self.homework_data()
        data.update({
            'subject': self.other_subject.pk, 'study_group': self.other_group.pk,
            'issue_at': '2000-01-01', 'deadline': '2000-01-02',
            'description': 'Updated description', 'penalty_info': 'Updated penalty',
            'teacher': self.other_teacher.pk,
        })
        response = self.client.get(self.edit_url)
        locked_fields = re.findall(
            r'<(?:input|select)[^>]*name="([^"]+)"[^>]*\bdisabled\b', response.content.decode()
        )
        for field_name in ['subject', 'study_group', 'issue_at', 'deadline']:
            self.assertIn(field_name, locked_fields)
        self.assertRedirects(self.client.post(self.edit_url, data), reverse('homework:teacher'))
        original_deadline = self.homework.deadline
        self.homework.refresh_from_db()
        self.assertEqual(self.homework.deadline, original_deadline)
        self.assertEqual(self.homework.issue_at, timezone.localdate())
        self.assertEqual(self.homework.study_group, self.group)
        self.assertEqual(self.homework.subject, self.subject)
        self.assertEqual(self.homework.teacher, self.teacher)
        self.assertEqual(self.homework.description, 'Updated description')
        self.assertEqual(self.homework.penalty_info, 'Updated penalty')
        self.submission.refresh_from_db()
        self.submission.full_clean()

    def test_stale_edit_form_cannot_change_group_after_student_submits(self):
        url = reverse('homework:teacher_homework_edit', args=[self.empty_homework.pk])
        self.client.get(url)
        Submission.objects.create(
            student=self.other_student, homework=self.empty_homework, answer_text='New response'
        )
        self.client.post(url, self.homework_data())
        self.empty_homework.refresh_from_db()
        self.assertEqual(self.empty_homework.study_group, self.other_group)
        self.assertEqual(self.empty_homework.subject, self.other_subject)

    def test_two_teachers_cannot_open_or_post_to_foreign_objects(self):
        for teacher, homework, submission in [
            (self.teacher, self.foreign_homework, self.foreign_submission),
            (self.other_teacher, self.homework, self.submission),
        ]:
            self.client.force_login(teacher)
            urls = [
                reverse('homework:teacher_homework_edit', args=[homework.pk]),
                reverse('homework:teacher_submissions', args=[homework.pk]),
                reverse('homework:teacher_grade', args=[submission.pk]),
            ]
            for url in urls:
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {'grade': 5, **self.homework_data()}).status_code, 404)
        self.foreign_submission.refresh_from_db()
        self.assertEqual(self.foreign_submission.grade, 4)
        self.submission.refresh_from_db()
        self.assertIsNone(self.submission.grade)

    def test_students_and_guests_cannot_use_teacher_functions(self):
        urls = [self.create_url, self.edit_url, self.answers_url, self.grade_url]
        self.client.logout()
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
            self.assertEqual(self.client.post(url, {'grade': 5}).status_code, 302)
        self.client.force_login(self.student)
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {'grade': 5}).status_code, 403)

    def test_each_action_requires_its_model_permission(self):
        for url, codename in [
            (self.create_url, 'add_homework'), (self.edit_url, 'change_homework'),
            (self.answers_url, 'view_submission'), (self.grade_url, 'change_submission'),
        ]:
            permission = Permission.objects.get(codename=codename)
            self.teacher.user_permissions.remove(permission)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {'grade': 5}).status_code, 403)
            self.teacher.user_permissions.add(permission)

    def test_dashboard_hides_actions_without_permissions(self):
        self.teacher.user_permissions.clear()
        response = self.client.get(reverse('homework:teacher'))
        self.assertNotContains(response, self.homework.description)
        for label in ['Создать домашнее задание', 'Редактировать', 'Посмотреть ответы']:
            self.assertNotContains(response, label)
        self.teacher.user_permissions.add(Permission.objects.get(codename='view_submission'))
        response = self.client.get(self.answers_url)
        self.assertNotContains(response, self.grade_url)

    def test_answers_include_student_text_time_status_and_grade(self):
        response = self.client.get(self.answers_url)
        for value in [self.student.get_full_name(), self.submission.answer_text, 'Сдано в срок', 'Не проверено']:
            self.assertContains(response, value)
        self.assertNotContains(response, self.foreign_submission.answer_text)
        self.assertContains(response, self.grade_url)

    def test_grade_form_changes_only_grade_and_both_interfaces_stay_in_sync(self):
        original_time = self.submission.submitted_at
        response = self.client.post(self.grade_url, {
            'grade': 5, 'answer_text': 'Forged', 'student': self.other_student.pk,
            'homework': self.foreign_homework.pk, 'submitted_at': '2000-01-01',
        })
        self.assertRedirects(response, self.answers_url)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.grade, 5)
        self.assertEqual(self.submission.answer_text, 'Private pupil answer')
        self.assertEqual(self.submission.student, self.student)
        self.assertEqual(self.submission.homework, self.homework)
        self.assertEqual(self.submission.submitted_at, original_time)
        admin_url = reverse('admin:homework_submission_change', args=[self.submission.pk])
        response = self.client.get(admin_url)
        self.assertEqual(response.context['adminform'].form.instance.grade, 5)
        self.assertEqual(set(response.context['adminform'].form.fields), {'grade'})
        response = self.client.post(admin_url, {
            'grade': 4, 'answer_text': 'Forged admin text', 'student': self.other_student.pk,
            'homework': self.foreign_homework.pk, '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.grade, 4)
        self.assertEqual(self.submission.answer_text, 'Private pupil answer')
        self.assertEqual(self.submission.submitted_at, original_time)
        self.assertEqual(self.submission.student, self.student)
        self.assertEqual(self.submission.homework, self.homework)
        self.assertContains(self.client.get(self.answers_url), 'Оценка:</strong> 4')
        self.client.force_login(self.student)
        for url in [reverse('homework:homeworks'), reverse('homework:homework_detail', args=[self.homework.pk])]:
            response = self.client.get(url)
            self.assertContains(response, 'Оценка:</strong> 4')
            self.assertContains(response, 'Сдано в срок')

    def test_grade_create_and_change_report_success_and_preserve_submission(self):
        original_time = self.submission.submitted_at
        original_count = Submission.objects.count()
        student_client = Client()
        student_client.force_login(self.student)
        for grade in [5, 4]:
            response = self.client.post(self.grade_url, {'grade': grade}, follow=True)
            self.assertContains(response, 'Оценка сохранена.')
            self.submission.refresh_from_db()
            self.assertEqual(self.submission.grade, grade)
            self.assertEqual(Submission.objects.count(), original_count)
            self.assertEqual(self.submission.student, self.student)
            self.assertEqual(self.submission.homework, self.homework)
            self.assertEqual(self.submission.answer_text, 'Private pupil answer')
            self.assertEqual(self.submission.submitted_at, original_time)
            for url in [reverse('homework:homeworks'), reverse('homework:homework_detail', args=[self.homework.pk])]:
                self.assertContains(student_client.get(url), 'Оценка:</strong> ' + str(grade))

    def test_grading_staff_author_returns_form_error(self):
        self.student.is_staff = True
        self.student.save()
        form = GradeForm({'grade': 5}, instance=self.submission)
        self.assertEqual(set(form.fields), {'grade'})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        response = self.client.post(self.grade_url, {'grade': 5})
        self.assertContains(response, 'Преподаватель не должен сдавать домашнее задание')
        self.assertContains(response, 'Текущая оценка:</strong> Не проверено')
        self.submission.refresh_from_db()
        self.assertIsNone(self.submission.grade)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_staff)

    def test_grading_author_without_profile_returns_form_error(self):
        self.student.student_profile.delete()
        response = self.client.post(self.grade_url, {'grade': 5})
        self.assertContains(response, 'У пользователя нет профиля ученика')
        self.submission.refresh_from_db()
        self.assertIsNone(self.submission.grade)

    def test_grading_author_from_another_group_returns_form_error(self):
        profile = self.student.student_profile
        profile.study_group = self.other_group
        profile.save()
        response = self.client.post(self.grade_url, {'grade': 5})
        self.assertContains(response, 'Это задание для другой группы')
        self.submission.refresh_from_db()
        self.assertIsNone(self.submission.grade)

    def test_admin_grading_invalid_author_returns_form_error(self):
        self.student.is_staff = True
        self.student.save()
        url = reverse('admin:homework_submission_change', args=[self.submission.pk])
        response = self.client.post(url, {'grade': 5, '_save': 'Save'})
        self.assertContains(response, 'Преподаватель не должен сдавать домашнее задание')
        self.submission.refresh_from_db()
        self.assertIsNone(self.submission.grade)

    def test_missing_submission_returns_404(self):
        url = reverse('homework:teacher_grade', args=[999999])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {'grade': 5}).status_code, 404)

    def test_student_submission_appears_in_workspace_and_can_be_graded(self):
        self.client.force_login(self.other_student)
        student_url = reverse('homework:homework_detail', args=[self.empty_homework.pk])
        self.assertRedirects(self.client.post(student_url, {'answer_text': 'Fresh student answer'}), student_url)
        submission = Submission.objects.get(student=self.other_student, homework=self.empty_homework)
        self.client.force_login(self.teacher)
        answers_url = reverse('homework:teacher_submissions', args=[self.empty_homework.pk])
        self.assertContains(self.client.get(answers_url), 'Fresh student answer')
        grade_url = reverse('homework:teacher_grade', args=[submission.pk])
        self.assertRedirects(self.client.post(grade_url, {'grade': 5}), answers_url)
        self.client.force_login(self.other_student)
        self.assertContains(self.client.get(student_url), 'Оценка:</strong> 5')

    def test_grades_follow_existing_model_validators(self):
        for grade in ['', '1', '6', 'not a number']:
            response = self.client.post(self.grade_url, {'grade': grade})
            self.assertContains(response, 'class="errorlist')
            self.assertContains(response, 'Текущая оценка:</strong> Не проверено')
            self.submission.refresh_from_db()
            self.assertIsNone(self.submission.grade)
        for grade in [2, 3, 4, 5]:
            self.assertRedirects(self.client.post(self.grade_url, {'grade': grade}), self.answers_url)
            self.submission.refresh_from_db()
            self.assertEqual(self.submission.grade, grade)

    def test_admin_scopes_lists_and_direct_urls_for_both_teachers(self):
        for teacher, own, foreign in [
            (self.teacher, self.homework, self.foreign_homework),
            (self.other_teacher, self.foreign_homework, self.homework),
        ]:
            self.client.force_login(teacher)
            response = self.client.get(reverse('admin:homework_homework_changelist'))
            ids = list(response.context['cl'].queryset.values_list('pk', flat=True))
            self.assertIn(own.pk, ids)
            self.assertNotIn(foreign.pk, ids)
            foreign_submission = Submission.objects.get(homework=foreign)
            response = self.client.get(reverse('admin:homework_submission_changelist'))
            ids = list(response.context['cl'].queryset.values_list('pk', flat=True))
            self.assertNotIn(foreign_submission.pk, ids)
            for url in [
                reverse('admin:homework_homework_change', args=[foreign.pk]),
                reverse('admin:homework_submission_change', args=[foreign_submission.pk]),
            ]:
                self.assertIn(self.client.get(url).status_code, [302, 403, 404])
                self.assertIn(self.client.post(url, {'grade': 2, **self.homework_data()}).status_code, [302, 403, 404])
        self.homework.refresh_from_db()
        self.foreign_homework.refresh_from_db()
        self.assertEqual(self.homework.description, 'Own assignment with an answer')
        self.assertEqual(self.foreign_homework.description, 'Other teacher private assignment')
        self.foreign_submission.refresh_from_db()
        self.assertEqual(self.foreign_submission.grade, 4)

    def test_admin_create_assigns_teacher_and_locks_submitted_homework(self):
        data = self.homework_data()
        data['teacher'] = self.other_teacher.pk
        response = self.client.post(reverse('admin:homework_homework_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Homework.objects.get(description=data['description']).teacher, self.teacher)
        data.update({
            'description': 'Admin edited text', 'subject': self.other_subject.pk,
            'study_group': self.other_group.pk, 'issue_at': '2000-01-01', 'deadline': '2000-01-02',
        })
        response = self.client.post(reverse('admin:homework_homework_change', args=[self.homework.pk]), data)
        self.assertEqual(response.status_code, 302)
        deadline = self.homework.deadline
        self.homework.refresh_from_db()
        self.assertEqual(self.homework.teacher, self.teacher)
        self.assertEqual(self.homework.study_group, self.group)
        self.assertEqual(self.homework.subject, self.subject)
        self.assertEqual(self.homework.deadline, deadline)
        self.assertEqual(self.homework.description, 'Admin edited text')

    def test_superuser_keeps_admin_access_to_all_objects(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin:homework_homework_changelist'))
        ids = list(response.context['cl'].queryset.values_list('pk', flat=True))
        self.assertIn(self.homework.pk, ids)
        self.assertIn(self.foreign_homework.pk, ids)
        for submission in [self.submission, self.foreign_submission]:
            url = reverse('admin:homework_submission_change', args=[submission.pk])
            self.assertEqual(self.client.get(url).status_code, 200)
            response = self.client.post(url, {
                'grade': 5, 'student': self.student.pk, 'homework': submission.homework_id,
                'answer_text': submission.answer_text, '_save': 'Save',
            })
            self.assertEqual(response.status_code, 302)
            submission.refresh_from_db()
            self.assertEqual(submission.grade, 5)

    def test_teacher_cannot_add_or_delete_student_submissions_in_admin(self):
        self.teacher.user_permissions.add(*Permission.objects.filter(
            codename__in=['add_submission', 'delete_submission'], content_type__app_label='homework'
        ))
        self.assertEqual(self.client.get(reverse('admin:homework_submission_add')).status_code, 403)
        url = reverse('admin:homework_submission_delete', args=[self.submission.pk])
        self.assertEqual(self.client.post(url, {'post': 'yes'}).status_code, 403)
        self.assertTrue(Submission.objects.filter(pk=self.submission.pk).exists())

    def test_teacher_forms_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.teacher)
        for url, data in [
            (self.create_url, self.homework_data()), (self.edit_url, self.homework_data()),
            (self.grade_url, {'grade': 5}),
        ]:
            client.get(url)
            self.assertEqual(client.post(url, data).status_code, 403)
            data['csrfmiddlewaretoken'] = client.cookies['csrftoken'].value
            self.assertEqual(client.post(url, data).status_code, 302)


class HomeworkAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_user(
            username='admin', is_staff=True, is_superuser=True
        )
        cls.teacher = User.objects.create_user(username='teacher', is_staff=True)
        cls.student = User.objects.create_user(username='student')
        cls.other_student = User.objects.create_user(username='other_student')
        cls.group = StudyGroup.objects.create(group_name='Group 1')
        cls.other_group = StudyGroup.objects.create(group_name='Group 2')
        cls.subject = Subject.objects.create(subject_name='Programming')
        StudentProfile.objects.create(user=cls.student, study_group=cls.group)
        StudentProfile.objects.create(
            user=cls.other_student, study_group=cls.other_group
        )
        cls.homework = Homework.objects.create(
            description='Write a Python function.',
            issue_at=timezone.localdate(),
            deadline=timezone.localdate() + timedelta(days=7),
            subject=cls.subject,
            study_group=cls.group,
            teacher=cls.teacher,
        )
        cls.submission = Submission.objects.create(
            student=cls.student, homework=cls.homework, answer_text='My answer'
        )

    def test_valid_homework_and_submission(self):
        self.homework.full_clean()
        self.submission.full_clean()

    def test_deadline_cannot_precede_issue_date(self):
        self.homework.deadline = self.homework.issue_at - timedelta(days=1)
        with self.assertRaises(ValidationError) as error:
            self.homework.full_clean()
        self.assertIn('deadline', error.exception.message_dict)

    def test_teacher_must_be_staff(self):
        self.homework.teacher = self.student
        with self.assertRaises(ValidationError) as error:
            self.homework.full_clean()
        self.assertIn('teacher', error.exception.message_dict)

    def test_student_cannot_submit_another_groups_homework(self):
        self.submission.student = self.other_student
        with self.assertRaises(ValidationError) as error:
            self.submission.full_clean()
        self.assertIn('__all__', error.exception.message_dict)

    def test_staff_cannot_submit_homework(self):
        self.submission.student = self.teacher
        with self.assertRaises(ValidationError):
            self.submission.full_clean()

    def test_student_needs_profile(self):
        student_without_profile = get_user_model().objects.create_user(
            username='without_profile'
        )
        self.submission.student = student_without_profile
        with self.assertRaises(ValidationError):
            self.submission.full_clean()

    def test_duplicate_submission_is_rejected(self):
        duplicate = Submission(
            student=self.student, homework=self.homework, answer_text='Second answer'
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_grade_range(self):
        for grade in [1, 6]:
            self.submission.grade = grade
            with self.assertRaises(ValidationError) as error:
                self.submission.full_clean()
            self.assertIn('grade', error.exception.message_dict)

    def test_admin_pages_are_available(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 200)
        for model in [StudyGroup, Subject, StudentProfile, Homework, Submission]:
            name = model._meta.model_name
            for page in ['changelist', 'add']:
                url = reverse('admin:homework_' + name + '_' + page)
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_teacher_choices_include_only_staff(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin:homework_homework_add'))
        teachers = response.context['adminform'].form.fields['teacher'].queryset
        self.assertIn(self.teacher, teachers)
        self.assertNotIn(self.student, teachers)

    def test_teacher_needs_model_permissions(self):
        self.client.force_login(self.teacher)
        url = reverse('admin:homework_submission_changelist')
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_teacher_can_grade_with_group_permissions(self):
        teacher_group = Group.objects.create(name='Teachers')
        permissions = Permission.objects.filter(
            content_type__app_label='homework',
            codename__in=['view_submission', 'change_submission'],
        )
        teacher_group.permissions.set(permissions)
        self.teacher.groups.add(teacher_group)
        self.client.force_login(self.teacher)
        url = reverse('admin:homework_submission_change', args=[self.submission.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {
            'student': self.student.pk,
            'homework': self.homework.pk,
            'answer_text': self.submission.answer_text,
            'grade': 5,
            '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.grade, 5)

    def test_student_has_no_admin_access(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(
            response, reverse('admin:login') + '?next=' + reverse('admin:index')
        )


class AccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.password = secrets.token_urlsafe(24)
        cls.student = User.objects.create_user(
            username='student', first_name='Мария', password=cls.password
        )
        cls.teacher = User.objects.create_user(
            username='teacher', first_name='Ирина', password=cls.password, is_staff=True
        )
        cls.admin = User.objects.create_superuser(username='admin', password=cls.password)
        cls.group = StudyGroup.objects.create(group_name='М3210')
        cls.other_group = StudyGroup.objects.create(group_name='М3211')
        StudentProfile.objects.create(
            user=cls.student, study_group=cls.group, patronymic='Ивановна'
        )
        cls.subject = Subject.objects.create(subject_name='Программирование')
        cls.homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.group, teacher=cls.teacher,
            description='Написать функцию.\n<script>alert(1)</script>',
            penalty_info='При просрочке оценка снижается на один балл.',
            deadline=timezone.localdate() + timedelta(days=7),
        )
        cls.foreign_homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.other_group, teacher=cls.teacher,
            description='Задание другой группы: создать таблицу.',
            deadline=timezone.localdate() + timedelta(days=5),
        )

    def registration_data(self):
        return {
            'username': 'new_student',
            'first_name': 'Анна',
            'last_name': 'Иванова',
            'patronymic': 'Петровна',
            'email': 'anna@example.com',
            'study_group': self.group.pk,
            'password1': self.password,
            'password2': self.password,
        }

    def test_guest_sees_welcome_and_account_links(self):
        response = self.client.get(reverse('homework:index'))
        self.assertContains(response, 'Доска домашних заданий')
        self.assertContains(response, reverse('homework:login'))
        self.assertContains(response, reverse('homework:register'))
        self.assertNotContains(response, self.homework.description)

    def test_guest_cannot_open_protected_pages(self):
        for name in ['homeworks', 'teacher']:
            url = reverse('homework:' + name)
            response = self.client.get(url)
            self.assertRedirects(response, reverse('homework:login') + '?next=' + url)

    def test_registration_form_has_all_fields_and_database_groups(self):
        response = self.client.get(reverse('homework:register'))
        for name in self.registration_data():
            self.assertContains(response, 'name="' + name + '"')
        self.assertContains(response, self.group.group_name)
        self.assertContains(response, self.other_group.group_name)
        self.assertContains(response, '<select', count=1)
        for name in ['role', 'is_staff', 'is_superuser']:
            self.assertNotContains(response, 'name="' + name + '"')

    def test_registration_saves_user_and_profile_and_logs_in(self):
        data = self.registration_data()
        data.update({'is_staff': 'true', 'is_superuser': 'true', 'role': 'teacher'})
        response = self.client.post(reverse('homework:register'), data)
        self.assertRedirects(response, reverse('homework:homeworks'))
        user = get_user_model().objects.get(username='new_student')
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.user_permissions.exists())
        self.assertEqual(user.student_profile.study_group, self.group)
        self.assertEqual(user.student_profile.patronymic, data['patronymic'])
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_registration_checks_required_fields(self):
        for name in self.registration_data():
            data = self.registration_data()
            data[name] = ''
            response = self.client.post(reverse('homework:register'), data)
            self.assertContains(response, 'class="errorlist')
            self.assertFalse(get_user_model().objects.filter(username='new_student').exists())

    def test_registration_rejects_invalid_values(self):
        for changes in [
            {'username': 'student'},
            {'email': 'invalid email'},
            {'study_group': '999999'},
            {'study_group': 'arbitrary group name'},
            {'password2': self.password + 'mismatch'},
            {'password1': '123', 'password2': '123'},
        ]:
            data = self.registration_data()
            data.update(changes)
            response = self.client.post(reverse('homework:register'), data)
            self.assertContains(response, 'class="errorlist')
            self.assertEqual(StudentProfile.objects.count(), 1)
            self.assertEqual(get_user_model().objects.count(), 3)

    def test_registration_rolls_back_user_if_profile_creation_fails(self):
        with patch('homework.views.StudentProfile.objects.create', side_effect=IntegrityError):
            with self.assertRaises(IntegrityError):
                self.client.post(reverse('homework:register'), self.registration_data())
        self.assertFalse(get_user_model().objects.filter(username='new_student').exists())

    def test_authenticated_user_cannot_register_again(self):
        self.client.force_login(self.teacher)
        response = self.client.post(reverse('homework:register'), self.registration_data())
        self.assertRedirects(response, reverse('homework:index'), fetch_redirect_response=False)
        self.assertFalse(get_user_model().objects.filter(username='new_student').exists())

    def test_one_login_form_redirects_each_role(self):
        for user, target in [
            (self.student, reverse('homework:homeworks')),
            (self.teacher, reverse('homework:teacher')),
            (self.admin, reverse('admin:index')),
        ]:
            self.client.logout()
            response = self.client.post(reverse('homework:login'), {
                'username': user.username, 'password': self.password,
            }, follow=True)
            self.assertEqual(response.redirect_chain, [
                (reverse('homework:index'), 302), (target, 302),
            ])
            self.assertEqual(response.status_code, 200)

    def test_login_form_requests_only_username_and_password(self):
        response = self.client.get(reverse('homework:login'))
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        for name in ['first_name', 'last_name', 'patronymic', 'email', 'study_group', 'role']:
            self.assertNotContains(response, 'name="' + name + '"')

    def test_wrong_credentials_use_same_generic_error(self):
        errors = []
        for username in ['student', 'missing_user']:
            data = {'username': username, 'password': self.password + 'wrong'}
            form = AuthenticationForm(data=data)
            self.assertFalse(form.is_valid())
            errors.append(list(form.non_field_errors()))
            response = self.client.post(reverse('homework:login'), data)
            self.assertContains(response, 'class="errorlist')
            self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(errors[0], errors[1])

    def test_inactive_user_cannot_log_in(self):
        self.student.is_active = False
        self.student.save()
        response = self.client.post(reverse('homework:login'), {
            'username': self.student.username, 'password': self.password,
        })
        self.assertContains(response, 'class="errorlist')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_does_not_accept_role_or_redirect_from_request(self):
        response = self.client.post(reverse('homework:login'), {
            'username': self.student.username, 'password': self.password,
            'is_staff': 'true', 'next': 'https://example.com/',
        }, follow=True)
        self.assertEqual(response.redirect_chain[-1][0], reverse('homework:homeworks'))
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_staff)

    def test_authenticated_home_and_login_redirect_by_role(self):
        for user, target in [
            (self.student, reverse('homework:homeworks')),
            (self.teacher, reverse('homework:teacher')),
            (self.admin, reverse('admin:index')),
        ]:
            self.client.force_login(user)
            self.assertRedirects(self.client.get(reverse('homework:index')), target)
            self.assertRedirects(
                self.client.get(reverse('homework:login')), reverse('homework:index'),
                fetch_redirect_response=False,
            )

    def test_student_sees_only_profile_groups_homework(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('homework:homeworks'), {
            'study_group': self.other_group.pk, 'group': self.other_group.pk,
            'is_staff': 'true',
        })
        for value in [
            self.student.first_name, self.group.group_name, self.subject.subject_name,
            self.teacher.first_name, self.homework.penalty_info,
            self.homework.issue_at.strftime('%d.%m.%Y'),
            self.homework.deadline.strftime('%d.%m.%Y'),
        ]:
            self.assertContains(response, value)
        self.assertContains(response, 'class="homework-card"', count=1)
        self.assertNotContains(response, self.foreign_homework.description)
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>')
        self.assertNotContains(response, reverse('admin:index'))

    def test_homework_list_has_detail_links_only_for_own_group(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('homework:homeworks'))
        self.assertContains(response, 'Подробнее')
        self.assertContains(response, reverse('homework:homework_detail', args=[self.homework.pk]))
        self.assertNotContains(response, reverse('homework:homework_detail', args=[self.foreign_homework.pk]))

    def test_homework_detail_and_return_to_list(self):
        self.client.force_login(self.student)
        url = reverse('homework:homework_detail', args=[self.homework.pk])
        response = self.client.get(url)
        for value in [
            self.subject.subject_name, self.teacher.first_name, self.group.group_name,
            self.homework.issue_at.strftime('%d.%m.%Y'),
            self.homework.deadline.strftime('%d.%m.%Y'),
            self.homework.penalty_info, 'Написать функцию.',
        ]:
            self.assertContains(response, value)
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>')
        self.assertContains(response, 'Назад к списку заданий')
        self.assertContains(response, 'href="' + reverse('homework:homeworks') + '"')
        self.assertContains(self.client.get(reverse('homework:homeworks')), self.group.group_name)

    def test_homework_detail_without_penalties(self):
        self.homework.penalty_info = ''
        self.homework.save()
        self.client.force_login(self.student)
        response = self.client.get(reverse('homework:homework_detail', args=[self.homework.pk]))
        self.assertContains(response, 'Штрафы не предусмотрены')

    def test_foreign_and_missing_homework_return_404(self):
        self.client.force_login(self.student)
        for pk in [self.foreign_homework.pk, 999999]:
            response = self.client.get(reverse('homework:homework_detail', args=[pk]), {
                'group': self.other_group.pk, 'study_group': self.other_group.pk,
            })
            self.assertEqual(response.status_code, 404)
            self.assertNotContains(response, self.foreign_homework.description, status_code=404)

    def test_homework_detail_requires_login(self):
        url = reverse('homework:homework_detail', args=[self.homework.pk])
        self.assertRedirects(
            self.client.get(url), reverse('homework:login') + '?next=' + url
        )

    def test_homework_detail_denies_staff_and_superuser(self):
        for user in [self.teacher, self.admin]:
            self.client.force_login(user)
            response = self.client.get(reverse('homework:homework_detail', args=[self.homework.pk]))
            self.assertEqual(response.status_code, 403)

    def test_homework_detail_requires_student_profile(self):
        user = get_user_model().objects.create_user(username='no_detail_profile')
        self.client.force_login(user)
        response = self.client.get(reverse('homework:homework_detail', args=[self.homework.pk]))
        self.assertEqual(response.status_code, 403)

    def test_empty_group_message(self):
        self.client.force_login(self.student)
        empty_group = StudyGroup.objects.create(group_name='Empty group')
        profile = self.student.student_profile
        profile.study_group = empty_group
        profile.save()
        response = self.client.get(reverse('homework:homeworks'))
        self.assertContains(response, 'Домашних заданий пока нет')

    def test_student_cannot_open_teacher_page_or_admin(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('homework:teacher')).status_code, 403)
        self.assertRedirects(
            self.client.get(reverse('admin:index')),
            reverse('admin:login') + '?next=' + reverse('admin:index'),
        )

    def test_user_without_profile_cannot_open_student_page(self):
        user = get_user_model().objects.create_user(username='without_profile')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('homework:homeworks')).status_code, 403)

    def test_teacher_without_profile_can_open_teacher_page(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('homework:teacher'))
        self.assertContains(response, self.teacher.first_name)
        self.assertContains(response, 'Вы вошли как преподаватель.')
        self.assertContains(response, reverse('admin:index'))
        self.assertFalse(StudentProfile.objects.filter(user=self.teacher).exists())
        self.assertEqual(self.client.get(reverse('homework:homeworks')).status_code, 403)

    def test_teacher_has_no_user_or_permission_management_access(self):
        self.client.force_login(self.teacher)
        for name in ['admin:auth_user_add', 'admin:auth_user_changelist', 'admin:auth_group_changelist']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_registration_and_logout_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('homework:register'))
        self.assertEqual(client.post(
            reverse('homework:register'), self.registration_data()
        ).status_code, 403)
        data = self.registration_data()
        data['csrfmiddlewaretoken'] = client.cookies['csrftoken'].value
        response = client.post(reverse('homework:register'), data)
        self.assertRedirects(response, reverse('homework:homeworks'))
        self.assertEqual(client.get(reverse('homework:logout')).status_code, 405)
        self.assertEqual(client.post(reverse('homework:logout')).status_code, 403)
        response = client.post(reverse('homework:logout'), {
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, reverse('homework:index'))
        self.assertNotIn('_auth_user_id', client.session)
        self.assertRedirects(
            client.get(reverse('homework:homeworks')),
            reverse('homework:login') + '?next=' + reverse('homework:homeworks'),
        )

    def test_login_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('homework:login'))
        data = {'username': self.student.username, 'password': self.password}
        self.assertEqual(client.post(reverse('homework:login'), data).status_code, 403)
        data['csrfmiddlewaretoken'] = client.cookies['csrftoken'].value
        response = client.post(reverse('homework:login'), data)
        self.assertRedirects(response, reverse('homework:index'), fetch_redirect_response=False)
        self.assertEqual(int(client.session['_auth_user_id']), self.student.pk)


class SubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username='submission_student')
        cls.classmate = User.objects.create_user(username='classmate')
        cls.teacher = User.objects.create_user(username='submission_teacher', is_staff=True)
        cls.admin = User.objects.create_user(username='submission_admin', is_staff=True, is_superuser=True)
        cls.group = StudyGroup.objects.create(group_name='Submission group')
        cls.other_group = StudyGroup.objects.create(group_name='Foreign group')
        StudentProfile.objects.create(user=cls.student, study_group=cls.group)
        StudentProfile.objects.create(user=cls.classmate, study_group=cls.group)
        cls.subject = Subject.objects.create(subject_name='Submission subject')
        cls.homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.group, teacher=cls.teacher,
            description='Answer this question',
            deadline=timezone.localdate() + timedelta(days=3),
        )
        cls.late_homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.group, teacher=cls.teacher,
            description='Late answers are allowed',
            issue_at=timezone.localdate() - timedelta(days=7),
            deadline=timezone.localdate() - timedelta(days=1),
        )
        cls.pending_homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.group, teacher=cls.teacher,
            description='Not submitted yet',
            deadline=timezone.localdate() + timedelta(days=5),
        )
        cls.foreign_homework = Homework.objects.create(
            subject=cls.subject, study_group=cls.other_group, teacher=cls.teacher,
            description='Foreign assignment',
            deadline=timezone.localdate() + timedelta(days=3),
        )

    def setUp(self):
        self.client.force_login(self.student)
        self.detail_url = reverse('homework:homework_detail', args=[self.homework.pk])

    def test_form_has_only_answer_field(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Мой ответ')
        self.assertContains(response, '<textarea')
        self.assertContains(response, 'name="answer_text"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'Сдать задание')
        for name in ['student', 'student_id', 'homework', 'grade', 'submitted_at']:
            self.assertNotContains(response, 'name="' + name + '"')

    def test_submit_saves_answer_and_hides_form(self):
        before = timezone.now()
        response = self.client.post(self.detail_url, {'answer_text': '  My answer\nSecond line  '})
        after = timezone.now()
        self.assertRedirects(response, self.detail_url)
        submission = Submission.objects.get(student=self.student, homework=self.homework)
        self.assertEqual(submission.answer_text, 'My answer\nSecond line')
        self.assertIsNone(submission.grade)
        self.assertGreaterEqual(submission.submitted_at, before)
        self.assertLessEqual(submission.submitted_at, after)
        response = self.client.get(self.detail_url)
        self.assertContains(response, submission.answer_text)
        self.assertContains(response, 'Сдано в срок')
        self.assertContains(response, 'Дата отправки:')
        self.assertContains(response, 'Оценка:</strong> На проверке')
        self.assertContains(
            self.client.get(reverse('homework:homeworks')), 'Оценка:</strong> На проверке'
        )
        self.assertNotContains(response, '<textarea')
        self.assertNotContains(response, 'Сдать задание')

    def test_empty_and_whitespace_answers_are_rejected(self):
        for answer in ['', '   ', '\n\t  ']:
            response = self.client.post(self.detail_url, {'answer_text': answer})
            self.assertContains(response, 'Введите текст ответа.')
            self.assertFalse(Submission.objects.exists())

    def test_metadata_from_post_is_ignored(self):
        before = timezone.now()
        response = self.client.post(self.detail_url, {
            'answer_text': 'An actual answer',
            'student': self.classmate.pk, 'student_id': self.classmate.pk,
            'homework': self.foreign_homework.pk, 'homework_id': self.foreign_homework.pk,
            'grade': 5, 'submitted_at': '2000-01-01T00:00:00Z',
        })
        self.assertRedirects(response, self.detail_url)
        submission = Submission.objects.get()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.homework, self.homework)
        self.assertIsNone(submission.grade)
        self.assertGreaterEqual(submission.submitted_at, before)

    def test_repeated_post_does_not_change_existing_answer(self):
        self.client.post(self.detail_url, {'answer_text': 'First answer'})
        original = Submission.objects.get()
        original.grade = 4
        original.save()
        response = self.client.post(self.detail_url, {'answer_text': 'Replacement', 'grade': 5})
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(Submission.objects.count(), 1)
        saved = Submission.objects.get()
        self.assertEqual(saved.answer_text, original.answer_text)
        self.assertEqual(saved.submitted_at, original.submitted_at)
        self.assertEqual(saved.grade, 4)

    def test_database_also_rejects_duplicate_submission(self):
        self.client.post(self.detail_url, {'answer_text': 'First answer'})
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Submission.objects.create(
                    student=self.student, homework=self.homework, answer_text='Duplicate'
                )
        self.assertEqual(Submission.objects.count(), 1)

    def test_model_validation_runs_before_saving(self):
        with patch('homework.views.Submission.full_clean', side_effect=ValidationError('Ответ не прошёл проверку.')):
            response = self.client.post(self.detail_url, {'answer_text': 'Answer'})
        self.assertContains(response, 'Ответ не прошёл проверку.')
        self.assertFalse(Submission.objects.exists())

    def test_integrity_error_has_friendly_message(self):
        with patch('homework.views.Submission.save', side_effect=IntegrityError):
            response = self.client.post(self.detail_url, {'answer_text': 'Answer'})
        self.assertContains(response, 'Не удалось сохранить ответ. Попробуйте ещё раз.')
        self.assertFalse(Submission.objects.exists())

    def test_late_submission_is_allowed(self):
        url = reverse('homework:homework_detail', args=[self.late_homework.pk])
        self.assertContains(self.client.get(url), 'Не сдано, срок истёк')
        response = self.client.post(url, {'answer_text': 'Late answer'})
        self.assertRedirects(response, url)
        self.assertContains(self.client.get(url), 'Сдано с опозданием')
        self.assertContains(self.client.get(url), 'Оценка:</strong> На проверке')
        self.assertIsNone(Submission.objects.get().grade)

    def test_status_uses_local_deadline_day_including_last_second(self):
        self.homework.deadline = date(2026, 10, 30)
        with timezone.override('Europe/Moscow'):
            for instant, expected in [
                ('2026-10-30T20:59:59+00:00', 'Сдано в срок'),
                ('2026-10-30T21:00:00+00:00', 'Сдано с опозданием'),
            ]:
                submission = Submission(submitted_at=datetime.fromisoformat(instant))
                self.assertEqual(get_submission_status(self.homework, submission), expected)

    def test_submission_time_is_displayed_in_django_timezone(self):
        submission = Submission.objects.create(
            student=self.student, homework=self.homework, answer_text='Answer'
        )
        Submission.objects.filter(pk=submission.pk).update(
            submitted_at=datetime.fromisoformat('2026-10-30T20:40:00+00:00')
        )
        with timezone.override('Europe/Moscow'):
            self.assertContains(self.client.get(self.detail_url), '30.10.2026, 23:40')

    def test_foreign_assignment_and_missing_assignment_reject_posts(self):
        for pk in [self.foreign_homework.pk, 999999]:
            response = self.client.post(reverse('homework:homework_detail', args=[pk]), {
                'answer_text': 'Forbidden answer', 'study_group': self.other_group.pk,
            })
            self.assertEqual(response.status_code, 404)
        self.assertFalse(Submission.objects.exists())

    def test_guest_staff_superuser_and_user_without_profile_cannot_submit(self):
        self.client.logout()
        response = self.client.post(self.detail_url, {'answer_text': 'Guest answer'})
        self.assertRedirects(response, reverse('homework:login') + '?next=' + self.detail_url)
        no_profile = get_user_model().objects.create_user(username='no_submission_profile')
        for user in [self.teacher, self.admin, no_profile]:
            self.client.force_login(user)
            response = self.client.post(self.detail_url, {'answer_text': 'Forbidden'})
            self.assertEqual(response.status_code, 403)
        self.assertFalse(Submission.objects.exists())

    def test_classmates_cannot_read_or_overwrite_each_others_answers(self):
        other_submission = Submission.objects.create(
            student=self.classmate, homework=self.homework, answer_text='Private classmate answer'
        )
        response = self.client.get(self.detail_url, {'submission': other_submission.pk})
        self.assertNotContains(response, other_submission.answer_text)
        self.assertContains(response, 'Сдать задание')
        self.assertContains(response, 'Статус:</strong> Не сдано')
        response = self.client.post(self.detail_url, {
            'answer_text': 'My own answer', 'submission': other_submission.pk,
        })
        self.assertRedirects(response, self.detail_url)
        other_submission.refresh_from_db()
        self.assertEqual(other_submission.answer_text, 'Private classmate answer')
        self.assertEqual(Submission.objects.count(), 2)
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'My own answer')
        self.assertNotContains(response, other_submission.answer_text)

    def test_list_shows_personal_submission_statuses(self):
        self.client.post(self.detail_url, {'answer_text': 'On-time answer'})
        self.client.post(reverse('homework:homework_detail', args=[self.late_homework.pk]), {
            'answer_text': 'Late answer',
        })
        response = self.client.get(reverse('homework:homeworks'))
        for status in ['Не сдано', 'Сдано в срок', 'Сдано с опозданием']:
            self.assertContains(response, 'Статус:</strong> ' + status)
        self.client.force_login(self.classmate)
        response = self.client.get(reverse('homework:homeworks'))
        self.assertNotContains(response, 'Статус:</strong> Сдано в срок')
        self.assertNotContains(response, 'Статус:</strong> Сдано с опозданием')
        self.assertContains(response, 'Не сдано, срок истёк')

    def test_unsubmitted_homework_shows_dash_for_grade(self):
        for url, status in [
            (self.detail_url, 'Не сдано'),
            (reverse('homework:homework_detail', args=[self.late_homework.pk]), 'Не сдано, срок истёк'),
        ]:
            response = self.client.get(url)
            self.assertContains(response, 'Статус:</strong> ' + status)
            self.assertContains(response, 'Оценка:</strong> —')
        response = self.client.get(reverse('homework:homeworks'))
        self.assertContains(response, 'Оценка:</strong> —', count=3)
        self.assertNotContains(response, 'На проверке')

    def test_grade_is_reloaded_on_both_pages_and_after_new_session(self):
        self.client.post(self.detail_url, {'answer_text': 'Answer'})
        submission = Submission.objects.get()
        for grade, expected in [(4, '4'), (None, 'На проверке'), (2, '2')]:
            submission.grade = grade
            submission.save()
            for url in [reverse('homework:homeworks'), self.detail_url]:
                response = self.client.get(url)
                self.assertContains(response, 'Оценка:</strong> ' + expected)
                self.assertContains(response, 'Статус:</strong> Сдано в срок')
        self.client.logout()
        self.client.force_login(self.student)
        for url in [reverse('homework:homeworks'), self.detail_url]:
            self.assertContains(self.client.get(url), 'Оценка:</strong> 2')

    def test_students_see_only_their_own_grades(self):
        own_submission = Submission.objects.create(
            student=self.student, homework=self.homework, answer_text='My answer', grade=3
        )
        other_submission = Submission.objects.create(
            student=self.classmate, homework=self.homework, answer_text='Classmate answer', grade=5
        )
        for user, own, other in [
            (self.student, own_submission, other_submission),
            (self.classmate, other_submission, own_submission),
        ]:
            self.client.force_login(user)
            for url in [reverse('homework:homeworks'), self.detail_url]:
                response = self.client.get(url, {
                    'student': other.student_id, 'submission': other.pk, 'grade': other.grade,
                })
                self.assertContains(response, 'Оценка:</strong> ' + str(own.grade))
                self.assertNotContains(response, 'Оценка:</strong> ' + str(other.grade))
                self.assertNotContains(response, other.answer_text)
        other_submission.grade = None
        other_submission.save()
        for url in [reverse('homework:homeworks'), self.detail_url]:
            self.assertContains(self.client.get(url), 'Оценка:</strong> На проверке')
        third_student = get_user_model().objects.create_user(username='third_grade_student')
        StudentProfile.objects.create(user=third_student, study_group=self.group)
        self.client.force_login(third_student)
        for url in [reverse('homework:homeworks'), self.detail_url]:
            response = self.client.get(url)
            self.assertContains(response, 'Оценка:</strong> —')
            self.assertNotContains(response, 'На проверке')
            self.assertNotContains(response, 'Статус:</strong> Сдано в срок')

    def test_submitted_answer_is_escaped(self):
        self.client.post(self.detail_url, {'answer_text': '<script>alert(1)</script>'})
        response = self.client.get(self.detail_url)
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>')

    def test_submission_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        client.get(self.detail_url)
        self.assertEqual(client.post(self.detail_url, {'answer_text': 'Answer'}).status_code, 403)
        response = client.post(self.detail_url, {
            'answer_text': 'Answer',
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(Submission.objects.count(), 1)

    def test_put_and_delete_cannot_modify_submission(self):
        self.client.post(self.detail_url, {'answer_text': 'Original answer'})
        self.assertEqual(self.client.put(self.detail_url, 'Replacement').status_code, 405)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 405)
        self.assertEqual(Submission.objects.get().answer_text, 'Original answer')

    def test_teacher_can_see_new_submission_and_grade_it_in_admin(self):
        self.client.post(self.detail_url, {'answer_text': 'New student work'})
        submission = Submission.objects.get()
        self.teacher.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='homework',
            codename__in=['view_submission', 'change_submission'],
        ))
        self.client.force_login(self.teacher)
        url = reverse('admin:homework_submission_change', args=[submission.pk])
        response = self.client.get(reverse('admin:homework_submission_changelist'))
        self.assertContains(response, self.student.username)
        response = self.client.get(url)
        self.assertContains(response, 'New student work')
        self.assertEqual(response.context['adminform'].form.instance.submitted_at, submission.submitted_at)
        self.assertIsNone(response.context['adminform'].form.instance.grade)
        response = self.client.post(url, {
            'student': self.student.pk, 'homework': self.homework.pk,
            'answer_text': submission.answer_text, 'grade': 5, '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        submission.refresh_from_db()
        self.assertEqual(submission.grade, 5)
        self.client.force_login(self.student)
        for url in [reverse('homework:homeworks'), self.detail_url]:
            response = self.client.get(url)
            self.assertContains(response, 'Оценка:</strong> 5')
            self.assertContains(response, 'Статус:</strong> Сдано в срок')


class HomeworkFilteringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.teacher = User.objects.create_user(username='filter_teacher', is_staff=True)
        cls.other_teacher = User.objects.create_user(username='filter_other_teacher', is_staff=True)
        cls.teacher.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='homework',
            codename__in=['view_homework', 'view_submission', 'change_homework'],
        ))
        cls.student = User.objects.create_user(username='filter_student')
        cls.classmate = User.objects.create_user(username='filter_classmate')
        cls.group = StudyGroup.objects.create(group_name='Фильтр ИС-21')
        cls.other_group = StudyGroup.objects.create(group_name='Фильтр ИС-22')
        cls.forbidden_group = StudyGroup.objects.create(group_name='Недоступная группа')
        for user in [cls.student, cls.classmate]:
            StudentProfile.objects.create(user=user, study_group=cls.group)
        cls.subject = Subject.objects.create(subject_name='Математика')
        cls.database = Subject.objects.create(subject_name='Базы данных')
        cls.foreign_subject = Subject.objects.create(subject_name='Чужая дисциплина')
        cls.assignments = []
        for number in range(12):
            cls.assignments.append(Homework.objects.create(
                teacher=cls.teacher, study_group=cls.group, subject=cls.subject,
                description='Задача Python: вычислить факториал ' + str(number),
                deadline=timezone.localdate() + timedelta(days=2),
            ))
        cls.database_homework = Homework.objects.create(
            teacher=cls.teacher, study_group=cls.group, subject=cls.database,
            description='Запрос SQL', deadline=timezone.localdate() + timedelta(days=3),
        )
        cls.other_group_homework = Homework.objects.create(
            teacher=cls.teacher, study_group=cls.other_group, subject=cls.subject,
            description='Задача Python другой группы', deadline=timezone.localdate() + timedelta(days=2),
        )
        cls.foreign_homework = Homework.objects.create(
            teacher=cls.other_teacher, study_group=cls.forbidden_group, subject=cls.foreign_subject,
            description='Задача Python чужого преподавателя', deadline=timezone.localdate() + timedelta(days=2),
        )

    def setUp(self):
        self.client.force_login(self.student)
        self.student_url = reverse('homework:homeworks')
        self.teacher_url = reverse('homework:teacher')

    def homework_ids(self, response, teacher=False):
        cards = re.findall(r'<article class="homework-card">(.*?)</article>', response.content.decode(), re.S)
        pattern = r'/teacher/homeworks/(\d+)/edit/' if teacher else r'/homeworks/(\d+)/'
        ids = []
        for card in cards:
            ids.append(int(re.search(pattern, card).group(1)))
        return ids

    def submit(self, homework, user=None, grade=None, instant=None):
        submission = Submission.objects.create(
            student=user or self.student, homework=homework, answer_text='Ответ', grade=grade,
        )
        if instant:
            Submission.objects.filter(pk=submission.pk).update(submitted_at=instant)
        return submission

    def next_link(self, response):
        return unescape(re.search(r'href="([^"]+)">Далее</a>', response.content.decode()).group(1))

    def test_case_insensitive_search_matches_subject_and_description_for_both_roles(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            for query in ['математика', 'ФАКТОРИАЛ', 'pYtHoN']:
                response = self.client.get(url, {'q': query, 'group': self.group.pk})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(self.homework_ids(response, user.is_staff), [h.pk for h in self.assignments[:5]])
                self.assertContains(response, 'Страница 1 из 3')
                self.assertNotContains(response, 'Запрос SQL')
                self.assertNotContains(response, self.foreign_homework.description)

    def test_subject_options_and_filter_are_scoped_to_accessible_assignments(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            response = self.client.get(url, {'subject': self.database.pk})
            self.assertEqual(self.homework_ids(response, user.is_staff), [self.database_homework.pk])
            self.assertContains(response, 'Все дисциплины')
            self.assertNotContains(response, self.foreign_subject.subject_name)
            self.assertNotContains(response, 'class="pagination"')
            for value in ['invalid', '99999999', '-1', '9' * 100, self.foreign_subject.pk]:
                self.assertEqual(self.client.get(url, {'subject': value}).status_code, 404)

    def test_student_status_filters_and_personal_ownership(self):
        timely, late, overdue, pending = self.assignments[:4]
        Homework.objects.filter(pk=overdue.pk).update(
            issue_at=timezone.localdate() - timedelta(days=2), deadline=timezone.localdate() - timedelta(days=1),
        )
        self.submit(timely)
        self.submit(late, instant=timezone.now() + timedelta(days=4))
        self.submit(pending, user=self.classmate, grade=5)
        expected = {
            'submitted': [timely.pk, late.pk],
            'not_submitted': [overdue.pk] + [h.pk for h in self.assignments[3:7]],
        }
        for status, ids in expected.items():
            response = self.client.get(self.student_url, {'status': status})
            self.assertEqual(self.homework_ids(response), ids)
        self.client.force_login(self.classmate)
        response = self.client.get(self.student_url, {'status': 'submitted'})
        self.assertEqual(self.homework_ids(response), [pending.pk])
        self.assertContains(response, 'Оценка:</strong> 5')

    def test_status_filter_and_card_agree_at_local_midnight(self):
        timely, late = self.assignments[:2]
        Homework.objects.filter(pk__in=[timely.pk, late.pk]).update(deadline=date(2026, 10, 30))
        self.submit(timely, instant=datetime.fromisoformat('2026-10-30T20:59:59+00:00'))
        self.submit(late, instant=datetime.fromisoformat('2026-10-30T21:00:00+00:00'))
        with timezone.override('Europe/Moscow'):
            response = self.client.get(self.student_url, {'status': 'submitted'})
            self.assertEqual(self.homework_ids(response), [timely.pk, late.pk])
            for label in ['Сдано в срок', 'Сдано с опозданием']:
                self.assertContains(response, 'Статус:</strong> ' + label)
            self.assertContains(response, 'Оценка:</strong> На проверке', count=2)

    def test_unsubmitted_filter_includes_past_today_and_future_deadlines(self):
        past, today, future = self.assignments[:3]
        Homework.objects.filter(pk=past.pk).update(
            issue_at=timezone.localdate() - timedelta(days=2), deadline=timezone.localdate() - timedelta(days=1),
        )
        Homework.objects.filter(pk=today.pk).update(deadline=timezone.localdate())
        response = self.client.get(self.student_url, {
            'status': 'not_submitted', 'subject': self.subject.pk, 'q': 'факториал',
        })
        for homework in [past, today, future]:
            self.assertIn(homework.pk, self.homework_ids(response))
        self.assertContains(response, 'Статус:</strong> Не сдано, срок истёк')
        self.assertContains(response, 'Страница 1 из 3')
        status_select = re.search(
            r'<select[^>]*name="status".*?</select>', response.content.decode(), re.S,
        ).group(0)
        labels = re.findall(r'<option[^>]*>(.*?)</option>', status_select)
        self.assertEqual(labels, ['Все задания', 'Не сдано', 'Сдано'])
        for removed_status in ['overdue', 'on_time', 'late']:
            self.assertEqual(self.client.get(self.student_url, {'status': removed_status}).status_code, 404)
        response = self.client.get(self.student_url + self.next_link(response))
        self.assertEqual(self.homework_ids(response), [h.pk for h in self.assignments[5:10]])

    def test_teacher_review_statuses_do_not_duplicate_homework_or_change_response_count(self):
        self.client.force_login(self.teacher)
        first, second = self.assignments[:2]
        self.submit(first)
        self.submit(first, user=self.classmate, grade=5)
        self.submit(second, grade=4)
        for status, expected in [('submitted', [first.pk, second.pk]), ('ungraded', [first.pk])]:
            response = self.client.get(self.teacher_url, {'status': status})
            self.assertEqual(self.homework_ids(response, True), expected)
            self.assertContains(response, 'Отправили ответы: 2')
        response = self.client.get(self.teacher_url, {'status': 'no_submissions', 'group': self.group.pk})
        self.assertEqual(self.homework_ids(response, True), [h.pk for h in self.assignments[2:7]])
        self.assertContains(response, 'Отправили ответы: 0', count=5)

    def test_all_teacher_filters_combine_and_keep_selected_values(self):
        self.client.force_login(self.teacher)
        self.submit(self.assignments[0])
        self.submit(self.database_homework)
        self.submit(self.other_group_homework)
        filters = {'q': '  ФАКТОРИАЛ  ', 'subject': self.subject.pk, 'group': self.group.pk, 'status': 'ungraded'}
        response = self.client.get(self.teacher_url, filters)
        self.assertEqual(self.homework_ids(response, True), [self.assignments[0].pk])
        self.assertContains(response, 'value="ФАКТОРИАЛ"')
        self.assertContains(response, '<option value="ungraded" selected>')
        for key in ['subject', 'group']:
            select = re.search(r'<select[^>]*name="' + key + r'".*?</select>', response.content.decode(), re.S).group(0)
            self.assertIn('<option value="' + str(filters[key]) + '" selected>', select)
        self.assertContains(response, '<select', count=3)
        self.assertContains(response, 'onchange="this.form.submit()"', count=3)

    def test_student_filters_combine(self):
        self.submit(self.assignments[0])
        self.submit(self.database_homework)
        response = self.client.get(self.student_url, {
            'q': 'факториал', 'subject': self.subject.pk, 'status': 'submitted',
        })
        self.assertEqual(self.homework_ids(response), [self.assignments[0].pk])
        self.assertContains(response, '<select', count=2)
        self.assertContains(response, 'onchange="this.form.submit()"', count=2)

    def test_twelve_filtered_assignments_paginate_five_five_two_in_stable_order(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            for page, start, end in [(1, 0, 5), (2, 5, 10), (3, 10, 12)]:
                response = self.client.get(url, {'q': 'факториал', 'group': self.group.pk, 'page': page})
                self.assertEqual(self.homework_ids(response, user.is_staff), [h.pk for h in self.assignments[start:end]])
                self.assertContains(response, 'Страница ' + str(page) + ' из 3')
                if page == 1:
                    self.assertContains(response, '<span class="pagination-disabled">Назад</span>', html=True)
                if page == 3:
                    self.assertContains(response, '<span class="pagination-disabled">Далее</span>', html=True)

    def test_pagination_links_preserve_encoded_search_and_all_filters(self):
        for user, url, status in [
            (self.student, self.student_url, 'not_submitted'),
            (self.teacher, self.teacher_url, 'no_submissions'),
        ]:
            self.client.force_login(user)
            filters = {'q': 'Задача Python', 'subject': str(self.subject.pk), 'status': status}
            if user.is_staff:
                filters['group'] = str(self.group.pk)
            response = self.client.get(url, filters)
            link = self.next_link(response)
            params = parse_qs(urlsplit(link).query)
            for key, value in filters.items():
                self.assertEqual(params[key], [value])
            self.assertEqual(params['page'], ['2'])
            response = self.client.get(url + link)
            self.assertEqual(self.homework_ids(response, user.is_staff), [h.pk for h in self.assignments[5:10]])
            self.assertContains(response, 'value="Задача Python"')

    def test_filter_form_omits_page_and_reset_returns_to_default_first_page(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            response = self.client.get(url, {'page': 3, 'q': 'факториал'})
            form = re.search(r'<form[^>]*class="homework-filter".*?</form>', response.content.decode(), re.S).group(0)
            self.assertNotIn('name="page"', form)
            self.assertIn('action="' + url + '"', form)
            self.assertIn('href="' + url + '">Сбросить фильтры</a>', form)
            self.assertIn('>Найти</button>', form)
            response = self.client.get(url, {'subject': self.database.pk})
            self.assertEqual(self.homework_ids(response, user.is_staff), [self.database_homework.pk])
            response = self.client.get(url)
            self.assertEqual(self.homework_ids(response, user.is_staff), [h.pk for h in self.assignments[:5]])
            self.assertContains(response, 'value="" placeholder="Введите предмет или текст задания"')

    def test_invalid_page_values_are_handled_by_paginator(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            for value, page in [('invalid', 1), ('0', 3), ('-1', 3), ('99999999', 3)]:
                response = self.client.get(url, {'q': 'факториал', 'page': value})
                self.assertContains(response, 'Страница ' + str(page) + ' из 3')

    def test_empty_results_have_message_and_no_pagination(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            response = self.client.get(url, {'q': 'Несуществующее задание', 'page': 3})
            self.assertContains(response, 'По вашему запросу домашние задания не найдены')
            self.assertNotContains(response, 'class="pagination"')
            self.assertEqual(self.homework_ids(response, user.is_staff), [])

    def test_parameters_cannot_override_teacher_or_student_scope(self):
        response = self.client.get(self.student_url, {'group': self.forbidden_group.pk, 'teacher': self.other_teacher.pk, 'q': 'чужого'})
        self.assertEqual(self.homework_ids(response), [])
        self.client.force_login(self.teacher)
        for group in [self.forbidden_group.pk, 'invalid', '99999999']:
            self.assertEqual(self.client.get(self.teacher_url, {'group': group}).status_code, 404)
        response = self.client.get(self.teacher_url, {'teacher': self.other_teacher.pk, 'q': 'чужого'})
        self.assertEqual(self.homework_ids(response, True), [])
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.teacher_url, {'status': 'ungraded'}).status_code, 403)
        self.client.logout()
        for url in [self.student_url, self.teacher_url]:
            self.assertEqual(self.client.get(url, {'q': 'Python'}).status_code, 302)

    def test_unknown_status_returns_404(self):
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(url, {'status': 'unknown'}).status_code, 404)

    def test_order_is_deadline_then_id(self):
        first, second = self.assignments[-2:]
        Homework.objects.filter(pk__in=[first.pk, second.pk]).update(deadline=timezone.localdate())
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            response = self.client.get(url)
            self.assertEqual(self.homework_ids(response, user.is_staff)[:2], [first.pk, second.pk])

    def test_search_special_characters_are_escaped_and_preserved_in_links(self):
        text = 'Факториал & Python + <пример>'
        Homework.objects.filter(pk__in=[h.pk for h in self.assignments]).update(description=text)
        for user, url in [(self.student, self.student_url), (self.teacher, self.teacher_url)]:
            self.client.force_login(user)
            response = self.client.get(url, {'q': text})
            self.assertContains(response, 'value="Факториал &amp; Python + &lt;пример&gt;"')
            self.assertEqual(parse_qs(urlsplit(self.next_link(response)).query)['q'], [text])
            self.assertNotContains(response, '<пример>')
