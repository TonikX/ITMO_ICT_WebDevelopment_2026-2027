from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SignUpForm, SubmissionForm
from .models import Homework, Subject, Submission


def signup_view(request):
    """Lets a new visitor create an account."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # creates the User row
            login(request, user)        # logs them in immediately, no extra step
            return redirect('homework_list')
    else:
        form = SignUpForm()
    return render(request, 'board/signup.html', {'form': form})


@login_required
def homework_list_view(request):
    """
    Shows every homework, newest deadline first.
    Supports filtering by subject (?subject=<id>) and pagination (?page=<n>).
    """
    homeworks = Homework.objects.select_related('subject').all()

    subject_id = request.GET.get('subject')
    if subject_id:
        homeworks = homeworks.filter(subject_id=subject_id)

    paginator = Paginator(homeworks, 5)  # 5 homeworks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'subjects': Subject.objects.all(),      # for the filter dropdown
        'selected_subject': subject_id,
    }
    return render(request, 'board/homework_list.html', context)


@login_required
def homework_detail_view(request, homework_id):
    """
    Shows one homework's full text. If the logged-in student already has
    a Submission for it, show that instead of the submit form.
    """
    homework = get_object_or_404(Homework, pk=homework_id)

    existing_submission = Submission.objects.filter(
        homework=homework, student=request.user
    ).first()

    if existing_submission:
        # Already submitted -> nothing more to do here, just display it
        return render(request, 'board/homework_detail.html', {
            'homework': homework,
            'submission': existing_submission,
        })

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)  # don't save to DB yet
            submission.homework = homework          # fill in the parts the form didn't ask for
            submission.student = request.user
            submission.save()
            return redirect('homework_detail', homework_id=homework.id)
    else:
        form = SubmissionForm()

    return render(request, 'board/homework_detail.html', {
        'homework': homework,
        'form': form,
    })


@login_required
def grades_list_view(request):
    """
    A table of every student's grades across all homeworks, as required
    by the assignment. Staff (teachers) additionally see a direct link
    to edit each row in Django Admin -- that's the "admin sees/can do
    more in the browser" requirement.
    """
    submissions = Submission.objects.select_related('student', 'homework', 'homework__subject').all()

    subject_id = request.GET.get('subject')
    if subject_id:
        submissions = submissions.filter(homework__subject_id=subject_id)

    paginator = Paginator(submissions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'subjects': Subject.objects.all(),
        'selected_subject': subject_id,
    }
    return render(request, 'board/grades_list.html', context)
