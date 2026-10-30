from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from .forms import GradeForm, HomeworkForm, StudentRegistrationForm, SubmissionForm
from .models import Homework, StudentProfile, StudyGroup, Subject, Submission


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        if request.user.is_staff:
            return redirect('homework:teacher')
        return redirect('homework:homeworks')
    return render(request, 'homework/index.html', using='jinja2')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('homework:index')
    form = StudentRegistrationForm()
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                StudentProfile.objects.create(
                    user=user,
                    patronymic=form.cleaned_data['patronymic'],
                    study_group=form.cleaned_data['study_group'],
                )
            login(request, user)
            return redirect('homework:homeworks')
    return render(
        request, 'homework/register.html', {'form': form}, using='jinja2'
    )


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('homework:index')
    form = AuthenticationForm(request=request)
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('homework:index')
    return render(request, 'homework/login.html', {'form': form}, using='jinja2')


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('homework:index')


def get_submission_status(homework, submission):
    if submission is None:
        if homework.deadline < timezone.localdate():
            return 'Не сдано, срок истёк'
        return 'Не сдано'
    if timezone.localdate(submission.submitted_at) <= homework.deadline:
        return 'Сдано в срок'
    return 'Сдано с опозданием'


def get_grade_display(submission):
    if submission is None:
        return '—'
    if submission.grade is None:
        return 'На проверке'
    return submission.grade


def paginate_homeworks(request, assignments):
    paginator = Paginator(assignments.order_by('deadline', 'pk'), 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    parameters = request.GET.copy()
    parameters.pop('page', None)
    return page_obj, parameters.urlencode()


@login_required
def homeworks(request):
    if request.user.is_staff or request.user.is_superuser:
        raise PermissionDenied('Эта страница предназначена для учеников.')
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        raise PermissionDenied('Профиль ученика не найден. Обратитесь к администратору.')
    assignments = Homework.objects.filter(study_group=profile.study_group).select_related(
        'subject', 'teacher'
    )
    subjects = Subject.objects.filter(
        homeworks__study_group=profile.study_group
    ).distinct().order_by('subject_name', 'pk')
    query = request.GET.get('q', '').strip()
    selected_subject = None
    subject_id = request.GET.get('subject', '')
    if subject_id:
        try:
            subject_id = int(subject_id)
        except ValueError:
            raise Http404('Дисциплина не найдена.')
        selected_subject = get_object_or_404(subjects, pk=subject_id)
        assignments = assignments.filter(subject=selected_subject)
    if query:
        assignments = assignments.filter(
            Q(subject__subject_name__icontains=query) | Q(description__icontains=query)
        )
    status = request.GET.get('status', '')
    status_labels = {
        'not_submitted': 'Не сдано',
        'submitted': 'Сдано',
    }
    if status and status not in status_labels:
        raise Http404('Неизвестный статус задания.')
    submissions = Submission.objects.filter(
        student=request.user, homework__study_group=profile.study_group
    )
    submissions_by_homework = {}
    for submission in submissions:
        submissions_by_homework[submission.homework_id] = submission
    if status == 'submitted':
        assignments = assignments.filter(pk__in=submissions_by_homework)
    elif status == 'not_submitted':
        assignments = assignments.exclude(pk__in=submissions_by_homework)
    page_obj, pagination_query = paginate_homeworks(request, assignments)
    for homework in page_obj:
        submission = submissions_by_homework.get(homework.pk)
        homework.submission_status = get_submission_status(homework, submission)
        homework.grade_display = get_grade_display(submission)
    return render(request, 'homework/homeworks.html', {
        'profile': profile,
        'homeworks': page_obj,
        'page_obj': page_obj, 'pagination_query': pagination_query,
        'subjects': subjects, 'selected_subject': selected_subject,
        'query': query, 'selected_status': status, 'status_labels': status_labels,
        'filters_active': bool(query or subject_id or status),
    }, using='jinja2')


@login_required
@require_http_methods(['GET', 'POST'])
def homework_detail(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        raise PermissionDenied('Эта страница предназначена для учеников.')
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        raise PermissionDenied('Профиль ученика не найден. Обратитесь к администратору.')
    homework = get_object_or_404(
        Homework.objects.select_related('subject', 'teacher', 'study_group'),
        pk=pk,
        study_group=profile.study_group,
    )
    submission = Submission.objects.filter(student=request.user, homework=homework).first()
    form = SubmissionForm()
    if request.method == 'POST':
        if submission is not None:
            return redirect('homework:homework_detail', pk=homework.pk)
        form = SubmissionForm(request.POST)
        if form.is_valid():
            new_submission = Submission(
                student=request.user,
                homework=homework,
                answer_text=form.cleaned_data['answer_text'],
            )
            try:
                with transaction.atomic():
                    new_submission.homework = Homework.objects.select_for_update().get(pk=homework.pk)
                    new_submission.full_clean()
                    new_submission.save()
            except ValidationError as error:
                if Submission.objects.filter(student=request.user, homework=homework).exists():
                    return redirect('homework:homework_detail', pk=homework.pk)
                form.add_error(None, error.messages)
            except IntegrityError:
                if Submission.objects.filter(student=request.user, homework=homework).exists():
                    return redirect('homework:homework_detail', pk=homework.pk)
                form.add_error(None, 'Не удалось сохранить ответ. Попробуйте ещё раз.')
            else:
                return redirect('homework:homework_detail', pk=homework.pk)
    submitted_at_local = None
    if submission is not None:
        submitted_at_local = timezone.localtime(submission.submitted_at)
    return render(request, 'homework/homework_detail.html', {
        'homework': homework,
        'submission': submission,
        'submission_status': get_submission_status(homework, submission),
        'grade_display': get_grade_display(submission),
        'submitted_at_local': submitted_at_local,
        'form': form,
    }, using='jinja2')


def check_teacher_access(user, permission=None):
    if not user.is_staff or user.is_superuser:
        raise PermissionDenied('Эта страница предназначена для преподавателей.')
    if permission and not user.has_perm(permission):
        raise PermissionDenied('Для этого действия необходимо разрешение администратора.')


def get_teacher_study_groups(user):
    return StudyGroup.objects.filter(homeworks__teacher=user).distinct().order_by('group_name', 'pk')


@login_required
def teacher(request):
    check_teacher_access(request.user)
    assignments = Homework.objects.none()
    study_groups = StudyGroup.objects.none()
    selected_group = None
    subjects = Subject.objects.none()
    selected_subject = None
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    status_labels = {
        'submitted': 'Есть отправленные ответы',
        'no_submissions': 'Нет отправленных ответов',
        'ungraded': 'Есть непроверенные ответы',
    }
    if request.user.has_perm('homework.view_homework'):
        study_groups = get_teacher_study_groups(request.user)
        assignments = Homework.objects.filter(teacher=request.user).select_related(
            'subject', 'study_group'
        ).annotate(submission_count=Count('submissions'))
        subjects = Subject.objects.filter(homeworks__teacher=request.user).distinct().order_by('subject_name', 'pk')
        group_id = request.GET.get('group', '')
        if group_id:
            try:
                group_id = int(group_id)
            except ValueError:
                raise Http404('Учебная группа не найдена.')
            selected_group = get_object_or_404(study_groups, pk=group_id)
            assignments = assignments.filter(study_group=selected_group)
        subject_id = request.GET.get('subject', '')
        if subject_id:
            try:
                subject_id = int(subject_id)
            except ValueError:
                raise Http404('Дисциплина не найдена.')
            selected_subject = get_object_or_404(subjects, pk=subject_id)
            assignments = assignments.filter(subject=selected_subject)
        if query:
            assignments = assignments.filter(
                Q(subject__subject_name__icontains=query) | Q(description__icontains=query)
            )
        if status == 'submitted':
            assignments = assignments.filter(submission_count__gt=0)
        elif status == 'no_submissions':
            assignments = assignments.filter(submission_count=0)
        elif status == 'ungraded':
            ungraded_homeworks = Submission.objects.filter(
                homework__teacher=request.user, grade__isnull=True
            ).values('homework_id')
            assignments = assignments.filter(pk__in=ungraded_homeworks)
        elif status:
            raise Http404('Неизвестный статус проверки.')
    elif request.GET.get('group'):
        raise PermissionDenied('Для просмотра заданий необходимо разрешение администратора.')
    page_obj, pagination_query = paginate_homeworks(request, assignments)
    return render(request, 'homework/teacher.html', {
        'homeworks': page_obj,
        'page_obj': page_obj, 'pagination_query': pagination_query,
        'study_groups': study_groups,
        'selected_group': selected_group,
        'subjects': subjects, 'selected_subject': selected_subject,
        'query': query, 'selected_status': status, 'status_labels': status_labels,
        'filters_active': bool(query or selected_group or selected_subject or status),
    }, using='jinja2')


@login_required
@require_http_methods(['GET', 'POST'])
def teacher_homework_form(request, pk=None):
    if pk is None:
        permission = 'homework.add_homework'
        title = 'Создать домашнее задание'
    else:
        permission = 'homework.change_homework'
        title = 'Редактировать домашнее задание'
    check_teacher_access(request.user, permission)
    with transaction.atomic():
        if pk is None:
            homework = Homework(teacher=request.user)
        else:
            assignments = Homework.objects.filter(teacher=request.user)
            if request.method == 'POST':
                assignments = assignments.select_for_update()
            homework = get_object_or_404(assignments, pk=pk)
        form = HomeworkForm(instance=homework)
        if request.method == 'POST':
            form = HomeworkForm(request.POST, instance=homework)
            if form.is_valid():
                form.save()
                return redirect('homework:teacher')
        return render(request, 'homework/teacher_homework_form.html', {
            'form': form, 'title': title,
        }, using='jinja2')


@login_required
def teacher_submissions(request, pk):
    check_teacher_access(request.user, 'homework.view_submission')
    homework = get_object_or_404(
        Homework.objects.select_related('subject', 'study_group'), pk=pk, teacher=request.user
    )
    submissions = Submission.objects.filter(homework=homework).select_related('student')
    for submission in submissions:
        submission.status_label = get_submission_status(homework, submission)
        submission.local_submitted_at = timezone.localtime(submission.submitted_at)
    return render(request, 'homework/teacher_submissions.html', {
        'homework': homework, 'submissions': submissions,
        'messages': messages.get_messages(request),
    }, using='jinja2')


@login_required
@require_http_methods(['GET', 'POST'])
def teacher_grade(request, pk):
    check_teacher_access(request.user, 'homework.change_submission')
    submission = get_object_or_404(
        Submission.objects.select_related('student', 'homework__subject', 'homework__study_group'),
        pk=pk, homework__teacher=request.user,
    )
    form = GradeForm(instance=submission)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.save(update_fields=['grade'])
            messages.success(request, 'Оценка сохранена.')
            return redirect('homework:teacher_submissions', pk=submission.homework_id)

        submission.refresh_from_db()
    return render(request, 'homework/teacher_grade.html', {
        'submission': submission, 'form': form,
        'submission_status': get_submission_status(submission.homework, submission),
        'submitted_at_local': timezone.localtime(submission.submitted_at),
    }, using='jinja2')


@login_required
@require_safe
def grades(request):
    requested_group = request.GET.get('group', '')
    group_id = None
    if requested_group:
        try:
            group_id = int(requested_group)
        except ValueError:
            raise Http404('Учебная группа не найдена.')

    available_groups = []
    study_group = None
    is_student = not request.user.is_staff and not request.user.is_superuser
    if is_student:
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            raise PermissionDenied('Профиль ученика не найден. Обратитесь к администратору.')
        study_group = profile.study_group
        if group_id is not None and group_id != study_group.pk:
            raise PermissionDenied('Доступен только журнал вашей учебной группы.')
        back_view = 'homework:homeworks'
    else:
        if request.user.is_superuser:
            available_groups = list(StudyGroup.objects.order_by('group_name', 'pk'))
            back_view = 'admin:index'
        else:
            check_teacher_access(request.user)
            if not request.user.has_perms(['homework.view_homework', 'homework.view_submission']):
                raise PermissionDenied('Для просмотра журнала нужны разрешения на просмотр заданий и сдач.')
            available_groups = list(get_teacher_study_groups(request.user))
            back_view = 'homework:teacher'
        if group_id is not None:
            for group in available_groups:
                if group.pk == group_id:
                    study_group = group
                    break
            if study_group is None:
                raise Http404('Учебная группа не найдена или недоступна.')
        elif available_groups:
            study_group = available_groups[0]

    students = []
    assignments = []
    rows = []
    if study_group is not None:
        students = list(StudentProfile.objects.filter(
            study_group=study_group, user__is_staff=False, user__is_superuser=False,
        ).order_by('user__last_name', 'user__first_name', 'user_id').values(
            'user_id', 'user__last_name', 'user__first_name', 'user__username', 'patronymic',
        ))
        assignments = list(Homework.objects.filter(study_group=study_group).select_related(
            'subject'
        ).order_by('subject__subject_name', 'deadline', 'pk'))
        student_ids = []
        for student in students:
            student_ids.append(student['user_id'])
        submissions = Submission.objects.filter(
            homework__study_group=study_group, student_id__in=student_ids,
        ).values_list('student_id', 'homework_id', 'grade')
        grades_by_pair = {}
        for student_id, homework_id, grade in submissions:
            grades_by_pair[(student_id, homework_id)] = grade
        for student in students:
            name_parts = []
            for field_name in ['user__last_name', 'user__first_name', 'patronymic']:
                if student[field_name]:
                    name_parts.append(student[field_name])
            name = ' '.join(name_parts)
            if not name:
                name = student['user__username']
            cells = []
            for homework in assignments:
                cells.append(grades_by_pair.get((student['user_id'], homework.pk)))
            rows.append({
                'name': name,
                'is_current_user': student['user_id'] == request.user.pk,
                'grades': cells,
            })
    return render(request, 'homework/grades.html', {
        'study_group': study_group, 'available_groups': available_groups,
        'homeworks': assignments, 'students': students, 'rows': rows,
        'is_student': is_student, 'back_view': back_view,
    }, using='jinja2')
