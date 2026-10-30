
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    StudentRegistrationForm,
    StudentLoginForm,
    SubmissionForm,
    GradeForm,
    AssignmentForm,
)

from .models import (
     Assignment,
    StudentProfile,
    Subject,
    Submission,
    SchoolClass,
)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = StudentRegistrationForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()

            StudentProfile.objects.create(
                user=user,
                school_class=form.cleaned_data["school_class"]
            )

        login(request, user)
        return redirect("home")

    return render(
        request,
        "homework/signup.html",
        {"form": form},
        using="jinja2"
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = StudentLoginForm(
        request,
        data=request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(
        request,
        "homework/login.html",
        {"form": form},
        using="jinja2"
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def assignment_list(request):
    query = request.GET.get("q", "").strip()
    selected_subject = request.GET.get("subject", "")

    assignments = Assignment.objects.select_related(
        "subject",
        "school_class",
        "created_by"
    )

    if not request.user.is_staff:
        profile = StudentProfile.objects.filter(
            user=request.user
        ).first()

        if profile:
            assignments = assignments.filter(
                school_class=profile.school_class
            )
        else:
            assignments = assignments.none()

    if query:
        assignments = assignments.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if selected_subject.isdigit():
        assignments = assignments.filter(
            subject_id=int(selected_subject)
        )

    subjects = Subject.objects.order_by("name")

    paginator = Paginator(assignments, 5)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "homework/assignments.html",
        {
            "page_obj": page_obj,
            "subjects": subjects,
            "query": query,
            "selected_subject": selected_subject,
        },
        using="jinja2"
    )


@login_required
def assignment_detail(request, pk):
    if request.user.is_staff:
        assignment = get_object_or_404(
            Assignment.objects.select_related(
                "subject",
                "school_class"
            ),
            pk=pk
        )
    else:
        profile = get_object_or_404(
            StudentProfile,
            user=request.user
        )

        assignment = get_object_or_404(
            Assignment.objects.select_related(
                "subject",
                "school_class"
            ),
            pk=pk,
            school_class=profile.school_class
        )

    submission = None
    submissions = []

    if request.user.is_staff:
        submissions = Submission.objects.filter(
            assignment=assignment
        ).select_related("student")
    else:
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()

    can_submit = (
        not request.user.is_staff
        and timezone.now() <= assignment.due_date
        and (
            submission is None
            or submission.grade is None
        )
    )

    form = None

    if not request.user.is_staff:
        form = SubmissionForm(
            request.POST if request.method == "POST" else None,
            instance=submission
        )

    if request.method == "POST":
        if not can_submit:
            raise PermissionDenied

        if form.is_valid():
            answer = form.save(commit=False)
            answer.assignment = assignment
            answer.student = request.user
            answer.save()

            return redirect(
                "assignment_detail",
                pk=pk
            )

    return render(
        request,
        "homework/assignment_detail.html",
        {
            "assignment": assignment,
            "submission": submission,
            "submissions": submissions,
            "form": form,
            "can_submit": can_submit,
        },
        using="jinja2"
    )


@login_required
def grade_submission(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    submission = get_object_or_404(
        Submission.objects.select_related(
            "assignment",
            "student"
        ),
        pk=pk
    )

    form = GradeForm(
        request.POST if request.method == "POST" else None,
        instance=submission
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        return redirect(
            "assignment_detail",
            pk=submission.assignment.pk
        )

    return render(
        request,
        "homework/grade_submission.html",
        {
            "submission": submission,
            "form": form,
        },
        using="jinja2"
    )


@login_required
def assignment_create(request):
    if not request.user.is_staff:
        raise PermissionDenied

    form = AssignmentForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.created_by = request.user
        assignment.save()

        return redirect(
            "assignment_detail",
            pk=assignment.pk
        )

    return render(
        request,
        "homework/assignment_form.html",
        {
            "form": form,
            "editing": False,
        },
        using="jinja2"
    )


@login_required
def assignment_edit(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    assignment = get_object_or_404(Assignment, pk=pk)

    form = AssignmentForm(
        request.POST if request.method == "POST" else None,
        instance=assignment
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        return redirect(
            "assignment_detail",
            pk=assignment.pk
        )

    return render(
        request,
        "homework/assignment_form.html",
        {
            "form": form,
            "editing": True,
        },
        using="jinja2"
    )


@login_required
def gradebook(request):
    classes = SchoolClass.objects.order_by("name")

    if request.user.is_staff:
        class_id = request.GET.get("school_class", "")

        if class_id.isdigit():
            selected_class = classes.filter(
                pk=int(class_id)
            ).first()
        else:
            selected_class = classes.first()
    else:
        profile = StudentProfile.objects.select_related(
            "school_class"
        ).filter(user=request.user).first()

        selected_class = (
            profile.school_class if profile else None
        )

    assignments = []
    rows = []

    if selected_class:
        assignments = list(
            Assignment.objects.filter(
                school_class=selected_class
            ).select_related("subject").order_by(
                "due_date", "pk"
            )
        )

        students = list(
            StudentProfile.objects.filter(
                school_class=selected_class
            ).select_related("user").order_by(
                "user__last_name",
                "user__first_name",
                "user__username"
            )
        )

        submissions = Submission.objects.filter(
            assignment__in=assignments,
            student_id__in=[
                student.user_id for student in students
            ]
        )

        submission_map = {
            (submission.student_id, submission.assignment_id):
                submission
            for submission in submissions
        }

        for student in students:
            cells = []

            for assignment in assignments:
                submission = submission_map.get(
                    (student.user_id, assignment.pk)
                )

                cells.append({
                    "submission": submission,
                    "grade": (
                        submission.grade if submission else None
                    ),
                })

            rows.append({
                "student": student.user,
                "cells": cells,
            })

    return render(
        request,
        "homework/gradebook.html",
        {
            "classes": classes,
            "selected_class": selected_class,
            "assignments": assignments,
            "rows": rows,
        },
        using="jinja2"
    )

