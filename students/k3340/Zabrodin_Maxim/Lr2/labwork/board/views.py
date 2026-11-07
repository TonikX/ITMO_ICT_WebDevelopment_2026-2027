from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Student_answer,  Homework, Subject
from .forms import AnswerForm,HomeworkForm, RegistrationForm
from django.contrib.auth import get_user_model, login
from django.core.paginator import Paginator
from django.db.models import Q

def homework_list(request):
    query = request.GET.get("q", "").strip()
    subject = request.GET.get("subject", "")

    homeworks = Homework.objects.select_related(
        "subject", "teacher"
    ).order_by("-issued_at", "-id")

    if query:
        homeworks = homeworks.filter(
            Q(text__icontains=query)
            | Q(subject__name__icontains=query)
        )

    if subject:
        homeworks = homeworks.filter(subject__name=subject)

    paginator = Paginator(homeworks, 5)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "homework_list.html", {
        "homeworks": page,
        "page": page,
        "subjects": Subject.objects.order_by("name"),
        "query": query,
        "selected_subject": subject,
    })

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("homework_list")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})

@login_required
def answer_submit(request, homework_id):
    if request.user.is_staff:
        raise PermissionDenied("Ответы отправляют только ученики.")

    homework = get_object_or_404(Homework, pk=homework_id)

    answer = Student_answer.objects.filter(
        homework=homework,
        student=request.user,
    ).first()

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.homework = homework
            answer.student = request.user
            answer.grade = None
            answer.save()
            return redirect("homework_list")
    else:
        form = AnswerForm(instance=answer)

    return render(request, "answer_form.html", {
        "form": form,
        "homework": homework,
    })

@login_required
def grade_table(request):
    User = get_user_model()

    students = User.objects.filter(
        is_staff=False,
        is_active=True,
    ).order_by("username")

    homeworks = list(
        Homework.objects.select_related("subject").order_by("id")
    )

    grades = {
        (answer.student_id, answer.homework_id): answer.grade
        for answer in Student_answer.objects.all()
    }

    rows = []
    for student in students:
        rows.append({
            "student": student,
            "grades": [
                grades.get((student.id, homework.id))
                for homework in homeworks
            ],
        })

    return render(request, "grade_table.html", {
        "homeworks": homeworks,
        "rows": rows,
    })

@login_required
def homework_create(request):
    if not request.user.is_staff:
        raise PermissionDenied("Создавать задания может только учитель.")

    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.teacher = request.user
            homework.save()
            return redirect("homework_list")
    else:
        form = HomeworkForm()

    return render(request, "homework_form.html", {"form": form})