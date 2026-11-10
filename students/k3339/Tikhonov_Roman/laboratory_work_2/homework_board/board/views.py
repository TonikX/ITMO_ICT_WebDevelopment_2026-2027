from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import HomeworkForm, RegisterForm, SubmissionForm
from .models import Homework, Subject, Submission

User = get_user_model()


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("homework_list")
    return render(request, "registration/register.html", {"form": form})


@login_required
def homework_list(request):
    queryset = (
        Homework.objects.select_related("subject", "teacher")
        .annotate(submissions_count=Count("submissions"))
        .order_by("-issued")
    )
    subject_id = request.GET.get("subject")
    query = request.GET.get("q")
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if query:
        queryset = queryset.filter(Q(text__icontains=query) | Q(subject__name__icontains=query))

    paginator = Paginator(queryset, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    submissions = {
        item.homework_id: item
        for item in Submission.objects.filter(
            student=request.user, homework_id__in=[hw.pk for hw in page_obj]
        )
    }
    rows = [(hw, submissions.get(hw.pk)) for hw in page_obj]

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "rows": rows,
        "page_obj": page_obj,
        "subjects": Subject.objects.all(),
        "subject_id": subject_id or "",
        "query": query or "",
        "page_query": ("?" + querystring + "&") if querystring else "?",
    }
    return render(request, "homework_list.html", context)


@login_required
def homework_detail(request, pk):
    homework = get_object_or_404(Homework.objects.select_related("subject", "teacher"), pk=pk)
    submission = Submission.objects.filter(homework=homework, student=request.user).first()

    if request.method == "POST" and not request.user.is_staff:
        form = SubmissionForm(request.POST)
        if form.is_valid():
            Submission.objects.update_or_create(
                homework=homework,
                student=request.user,
                defaults={"text": form.cleaned_data["text"]},
            )
            return redirect("homework_detail", pk=pk)
    else:
        form = SubmissionForm(initial={"text": submission.text if submission else ""})

    return render(
        request,
        "homework_detail.html",
        {
            "homework": homework,
            "form": form,
            "submission": submission,
            "submissions_count": homework.submissions.count(),
        },
    )


@login_required
def grades(request):
    homeworks = list(Homework.objects.select_related("subject").order_by("issued"))
    students = User.objects.filter(is_staff=False).order_by("last_name", "first_name")
    grades_map = {}
    for item in Submission.objects.all():
        grades_map.setdefault(item.homework_id, {})[item.student_id] = item.grade
    table = [(student, [grades_map.get(hw.pk, {}).get(student.pk) for hw in homeworks]) for student in students]
    return render(request, "grades.html", {"homeworks": homeworks, "table": table})


@user_passes_test(lambda u: u.is_staff)
def homework_create(request):
    form = HomeworkForm(request.POST or None)
    if form.is_valid():
        homework = form.save(commit=False)
        homework.teacher = request.user
        homework.save()
        return redirect("homework_list")
    return render(request, "homework_form.html", {"form": form})


@user_passes_test(lambda u: u.is_staff)
def homework_submissions(request, pk):
    homework = get_object_or_404(Homework.objects.select_related("subject"), pk=pk)
    submissions = homework.submissions.select_related("student").order_by("student__last_name")
    return render(
        request,
        "submissions.html",
        {"homework": homework, "submissions": submissions},
    )


@user_passes_test(lambda u: u.is_staff)
def submission_grade(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("homework"), pk=pk)
    if request.method == "POST":
        value = request.POST.get("grade", "").strip()
        try:
            submission.grade = int(value) if value else None
            submission.save()
        except ValueError:
            pass
    return redirect("homework_submissions", pk=submission.homework_id)
