from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Homework, Submission
from .forms import SubmissionForm, GradeForm

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Subject, Homework

def homework_list(request):
    homeworks = Homework.objects.select_related('subject', 'teacher').order_by('due_date')
    subjects = Subject.objects.all()

    search = request.GET.get('search', '').strip()
    subject_id = request.GET.get('subject', '')

    if search:
        homeworks = homeworks.filter(
            Q(description__icontains=search) |
            Q(subject__name__icontains=search)
        )

    if subject_id:
        homeworks = homeworks.filter(subject_id=subject_id)

    paginator = Paginator(homeworks, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'board/homework_list.html', {
        'page_obj': page_obj,
        'subjects': subjects,
        'search': search,
        'subject_id': subject_id,
    })


@login_required
def submit_homework(request, homework_id):
    homework = get_object_or_404(Homework, pk=homework_id)

    if request.user.is_staff:
        messages.error(request, 'Преподаватель не может сдавать задания.')
        return redirect('homework_list')

    if Submission.objects.filter(
        homework=homework,
        student=request.user
    ).exists():
        messages.info(request, 'Вы уже сдали это задание.')
        return redirect('homework_list')

    if request.method == 'POST':
        form = SubmissionForm(request.POST)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.homework = homework
            submission.student = request.user
            submission.save()

            messages.success(request, 'Работа успешно отправлена!')
            return redirect('homework_list')
    else:
        form = SubmissionForm()

    return render(request, 'board/submit_homework.html', {
        'form': form,
        'homework': homework
    })



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'board/register.html', {'form': form})


@login_required
def grade_list(request):
    if request.user.is_staff:
        students = User.objects.filter(is_staff=False).order_by('username')
    else:
        students = User.objects.filter(id=request.user.id)
    homeworks = list(Homework.objects.select_related('subject').order_by('id'))

    submissions = Submission.objects.all()

    grades = {}

    for submission in submissions:
        grades[(submission.student_id, submission.homework_id)] = submission.grade

    rows = []

    for student in students:
        student_grades = []

        for homework in homeworks:
            grade = grades.get((student.id, homework.id))

            if grade is None:
                student_grades.append('—')
            else:
                student_grades.append(grade)

        rows.append({
            'student': student,
            'grades': student_grades
        })

    return render(request, 'board/grade_list.html', {
        'homeworks': homeworks,
        'rows': rows
    })


@login_required
def teacher_submissions(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Доступ запрещён')

    submissions = Submission.objects.select_related(
        'student', 'homework__subject'
    ).order_by('-submitted_at')

    return render(request, 'board/teacher_submissions.html', {
        'submissions': submissions
    })


@login_required
def grade_submission(request, submission_id):
    if not request.user.is_staff:
        return HttpResponseForbidden('Доступ запрещён')

    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)

        if form.is_valid():
            form.save()
            messages.success(request, 'Оценка сохранена')
            return redirect('teacher_submissions')
    else:
        form = GradeForm(instance=submission)

    return render(request, 'board/grade_submission.html', {
        'form': form,
        'submission': submission
    })
