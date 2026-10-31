"""Контроллеры приложения "Доска домашних заданий"."""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import SubmissionForm, UserRegistrationForm
from .models import Homework, Profile, Submission


def is_teacher(user):
    """Преподаватель — сотрудник или суперпользователь."""
    return bool(user.is_authenticated and (user.is_staff or user.is_superuser))


def _paginate(request, queryset, page_size=None):
    """Разбивает QuerySet на страницы и возвращает объект Page."""
    page_size = page_size or 5
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    """Список всех домашних заданий: фильтр по предмету + поиск + пагинация."""
    queryset = Homework.objects.all()

    subject = request.GET.get('subject', '').strip()
    query = request.GET.get('q', '').strip()

    if subject:
        queryset = queryset.filter(subject=subject)
    if query:
        queryset = queryset.filter(Q(text__icontains=query) | Q(teacher__icontains=query))

    subjects = (
        Homework.objects.values_list('subject', flat=True)
        .distinct()
        .order_by('subject')
    )

    pages = _paginate(request, queryset)

    # Множество id заданий, которые текущий ученик уже сдал (для бейджа "Сдано").
    submitted_ids = set()
    if request.user.is_authenticated and not is_teacher(request.user):
        submitted_ids = set(
            Submission.objects
            .filter(student=request.user)
            .values_list('homework_id', flat=True)
        )

    context = {
        'pages': pages,
        'subjects': subjects,
        'current_subject': subject,
        'query': query,
        'submitted_ids': submitted_ids,
    }
    return render(request, 'homework/index.html', context)


def homework_detail(request, pk):
    """Страница задания."""
    homework = get_object_or_404(Homework, pk=pk)

    if is_teacher(request.user):
        submissions = homework.submissions.select_related('student').order_by('student__username')
        return render(
            request,
            'homework/homework_detail.html',
            {'homework': homework, 'submissions': submissions, 'is_teacher': True},
        )

    user_submission = (
        homework.submissions.filter(student=request.user).first()
        if request.user.is_authenticated else None
    )
    is_late = bool(request.user.is_authenticated
                   and user_submission
                   and _is_late(user_submission))

    if request.method == 'POST' and request.user.is_authenticated:
        action = request.POST.get('action')

        if action == 'submit' and user_submission is None:
            form = SubmissionForm(request.POST)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.homework = homework
                submission.student = request.user
                submission.save()
                messages.success(request, 'Решение отправлено на проверку.')
                return redirect('homework:homework_detail', pk=homework.pk)
            messages.error(request, 'Исправьте ошибки в форме.')

        elif action == 'update' and user_submission and user_submission.mark is None:
            form = SubmissionForm(request.POST, instance=user_submission)
            if form.is_valid():
                form.save()
                messages.success(request, 'Решение обновлено.')
                return redirect('homework:homework_detail', pk=homework.pk)
            messages.error(request, 'Исправьте ошибки в форме.')

        elif action == 'delete' and user_submission and user_submission.mark is None:
            user_submission.delete()
            messages.success(request, 'Решение удалено.')
            return redirect('homework:homework_detail', pk=homework.pk)

    form = SubmissionForm(instance=user_submission)
    context = {
        'homework': homework,
        'user_submission': user_submission,
        'form': form,
        'is_teacher': False,
        'is_late': is_late,
    }
    return render(request, 'homework/homework_detail.html', context)


@login_required
def my_submissions(request):
    """Все сданные работы текущего пользователя с отметками (пагинация)."""
    submissions = (
        Submission.objects
        .filter(student=request.user)
        .select_related('homework')
    )
    pages = _paginate(request, submissions)
    return render(request, 'homework/my_submissions.html', {'pages': pages})


def class_summary(request):
    """Сводка отметок класса."""
    teacher = is_teacher(request.user)
    groups = list(
        Profile.objects.exclude(group='')
        .values_list('group', flat=True)
        .distinct()
        .order_by('group')
    )

    if teacher:
        selected = request.GET.get('group', '')
        if selected not in groups and groups:
            selected = groups[0]
        if selected:
            base = Submission.objects.filter(student__profile__group=selected)
        else:
            base = Submission.objects.all()
    else:
        profile = getattr(request.user, 'profile', None)
        selected = profile.group if profile else ''
        # Ученик видит сводку своего класса; без группы — только свои работы.
        if not request.user.is_authenticated:
            base = Submission.objects.none()
        elif selected:
            base = Submission.objects.filter(student__profile__group=selected)
        else:
            base = Submission.objects.filter(student=request.user)

    rows = (
        base
        .values('homework_id', 'homework__subject')
        .annotate(
            total=Count('id'),
            graded=Count('mark'),
            avg_mark=Avg('mark'),
        )
        .order_by('homework_id')
    )
    # Добавляем читаемые поля задания для таблицы.
    homework_map = {h.pk: h for h in Homework.objects.all()}
    summary_rows = []
    for row in rows:
        hw = homework_map.get(row['homework_id'])
        summary_rows.append({
            'homework': hw,
            'total': row['total'],
            'graded': row['graded'],
            'avg_mark': round(row['avg_mark'], 2) if row['avg_mark'] is not None else None,
        })

    # Сводка по всем классам — видна только учителю.
    per_class = None
    if teacher:
        per_class = (
            Submission.objects
            .values('student__profile__group')
            .annotate(
                total=Count('id'),
                graded=Count('mark'),
                avg_mark=Avg('mark'),
            )
            .order_by('student__profile__group')
        )

    context = {
        'is_teacher': teacher,
        'groups': groups,
        'selected': selected,
        'summary_rows': summary_rows,
        'per_class': per_class,
    }
    return render(request, 'homework/class_summary.html', context)


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            form.save()
            messages.success(
                request,
                f'Регистрация {username} завершена. Теперь можно войти.',
            )
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'homework/register.html', {'form': form})


def _is_late(submission):
    """Решение сдано позже срока выполнения задания (deadline)."""
    deadline = submission.homework.deadline
    if deadline is None:
        return False
    end_of_deadline_day = timezone.make_aware(
        datetime.combine(deadline, datetime.min.time())
    )
    return submission.submitted_at > end_of_deadline_day
