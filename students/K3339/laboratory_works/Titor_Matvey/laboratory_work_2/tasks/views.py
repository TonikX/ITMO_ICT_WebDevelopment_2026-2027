from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import SignUpForm, WorkForm
from .models import StudentProfile, Task, Work


def staff_check(user):
    return bool(user.is_authenticated and (user.is_staff or user.is_superuser))


def pager(request, objects):
    return Paginator(objects, 7).get_page(request.GET.get('page'))


def task_list(request):
    objects = Task.objects.all()

    discipline = request.GET.get('discipline', '').strip()
    search = request.GET.get('find', '').strip()

    if discipline:
        objects = objects.filter(discipline=discipline)
    if search:
        objects = objects.filter(Q(body__icontains=search) | Q(teacher_name__icontains=search))

    disciplines = Task.objects.values_list('discipline', flat=True).distinct().order_by('discipline')
    page = pager(request, objects)

    done_ids = set()
    if request.user.is_authenticated and not staff_check(request.user):
        done_ids = set(Work.objects.filter(student=request.user).values_list('task_id', flat=True))

    context = {
        'page': page,
        'disciplines': disciplines,
        'discipline': discipline,
        'search': search,
        'done_ids': done_ids,
    }
    return render(request, 'tasks/list.html', context)


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if staff_check(request.user):
        works = task.works.select_related('student').order_by('student__username')
        return render(request, 'tasks/task.html', {'task': task, 'works': works, 'show_all': True})

    my_work = None
    if request.user.is_authenticated:
        my_work = task.works.filter(student=request.user).first()

    too_late = False
    if my_work and my_work.sent_at.date() > task.due_on:
        too_late = True

    if request.method == 'POST' and request.user.is_authenticated:
        button = request.POST.get('button')

        if button == 'send' and my_work is None:
            form = WorkForm(request.POST)
            if form.is_valid():
                work = form.save(commit=False)
                work.task = task
                work.student = request.user
                work.save()
                messages.success(request, 'Работа отправлена.')
                return redirect('tasks:task', pk=task.pk)
            messages.error(request, 'Проверьте правильность заполнения.')
            return render(request, 'tasks/task.html', {'task': task, 'form': form, 'show_all': False})

        if button == 'resend' and my_work and my_work.score is None:
            form = WorkForm(request.POST, instance=my_work)
            if form.is_valid():
                form.save()
                messages.success(request, 'Работа обновлена.')
                return redirect('tasks:task', pk=task.pk)
            messages.error(request, 'Проверьте правильность заполнения.')
            return render(request, 'tasks/task.html', {'task': task, 'form': form, 'show_all': False})

        if button == 'drop' and my_work and my_work.score is None:
            my_work.delete()
            messages.success(request, 'Работа удалена.')
            return redirect('tasks:task', pk=task.pk)

    form = WorkForm(instance=my_work)
    return render(request, 'tasks/task.html', {
        'task': task,
        'my_work': my_work,
        'form': form,
        'show_all': False,
        'too_late': too_late,
    })


@login_required
def my_works(request):
    works = Work.objects.filter(student=request.user).select_related('task')
    page = pager(request, works)
    return render(request, 'tasks/mine.html', {'page': page})


def class_stats(request):
    is_staff = staff_check(request.user)
    group_names = list(
        StudentProfile.objects.exclude(study_group='')
        .values_list('study_group', flat=True)
        .distinct()
        .order_by('study_group')
    )

    chosen = ''
    if is_staff:
        chosen = request.GET.get('group', '')
        if chosen and chosen not in group_names:
            chosen = group_names[0] if group_names else ''
        base = Work.objects.filter(student__card__study_group=chosen) if chosen else Work.objects.all()
    else:
        card = getattr(request.user, 'card', None)
        chosen = card.study_group if card else ''
        if chosen:
            base = Work.objects.filter(student__card__study_group=chosen)
        elif request.user.is_authenticated:
            base = Work.objects.filter(student=request.user)
        else:
            base = Work.objects.none()

    stat_rows = list(
        base.values('task_id')
        .annotate(total=Count('id'), checked=Count('score'), average=Avg('score'))
        .order_by('task_id')
    )
    tasks_map = {t.pk: t for t in Task.objects.all()}
    table = [
        {
            'task': tasks_map[row['task_id']],
            'total': row['total'],
            'checked': row['checked'],
            'average': round(row['average'], 2) if row['average'] is not None else None,
        }
        for row in stat_rows
    ]

    by_groups = None
    if is_staff:
        by_groups = list(
            Work.objects.values('student__card__study_group')
            .annotate(total=Count('id'), checked=Count('score'), average=Avg('score'))
            .order_by('student__card__study_group')
        )

    context = {
        'is_staff': is_staff,
        'group_names': group_names,
        'chosen': chosen,
        'table': table,
        'by_groups': by_groups,
    }
    return render(request, 'tasks/stats.html', context)


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['username']
        form.save()
        messages.success(request, f'Аккаунт {name} создан, теперь войдите.')
        return redirect('login')
    return render(request, 'tasks/signup.html', {'form': form})
