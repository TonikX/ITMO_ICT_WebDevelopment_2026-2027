from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import ConferenceReviewForm, TalkSubmissionForm
from .models import Conference, ConferenceReview, Location, TalkSubmission, Theme


def _style_form(form):
    for field in form:
        classes = field.field.widget.attrs.get("class", "")
        field.field.widget.attrs["class"] = f"{classes} form-control".strip()
        if field.errors:
            field.field.widget.attrs["class"] += " is-invalid"


class StyledLoginView(LoginView):
    template_name = "app/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        _style_form(form)
        return form


class RegistrationLogoutView(LogoutView):
    next_page = reverse_lazy("login")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        _style_form(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно. Теперь войдите в аккаунт.")
            return redirect("conference_list")
    else:
        form = UserCreationForm()
        _style_form(form)

    return render(request, "app/register.html", {"form": form})


def conference_list(request):
    conferences = Conference.objects.select_related("location").prefetch_related("themes")
    search_query = request.GET.get("q", "").strip()
    theme_id = request.GET.get("theme", "").strip()
    location_id = request.GET.get("location", "").strip()

    if search_query:
        conferences = conferences.filter(name__icontains=search_query)
    if theme_id.isdigit():
        conferences = conferences.filter(themes__id=int(theme_id))
    if location_id.isdigit():
        conferences = conferences.filter(location_id=int(location_id))

    conferences = conferences.order_by("start_date", "pk").distinct()
    paginator = Paginator(conferences, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "app/conference_list.html",
        {
            "page_obj": page_obj,
            "themes": Theme.objects.order_by("name"),
            "locations": Location.objects.order_by("name"),
            "selected_theme": theme_id,
            "selected_location": location_id,
            "search_query": search_query,
            "query_string": query_params.urlencode(),
        },
    )


@login_required(login_url="login")
def participant_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    participants = (
        TalkSubmission.objects.select_related("conference", "author")
        .order_by("conference__start_date", "conference__name", "author__username")
    )
    return render(
        request,
        "app/participant_list.html",
        {"participants": participants},
    )


def conference_detail(request, conference_id):
    conference = get_object_or_404(
        Conference.objects.select_related("location").prefetch_related("themes"),
        pk=conference_id,
    )
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                login_url=reverse_lazy("login"),
            )
        review_form = ConferenceReviewForm(request.POST)
        _style_form(review_form)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.conference = conference
            review.reviewer = request.user
            review.save()
            messages.success(request, "Ваш отзыв опубликован.")
            return redirect("conference_detail", conference_id=conference.pk)
    else:
        review_form = ConferenceReviewForm()
        _style_form(review_form)

    reviews = ConferenceReview.objects.filter(conference=conference).select_related(
        "reviewer"
    ).order_by("-created_at")
    recommended_submissions = (
        TalkSubmission.objects.filter(
            conference=conference,
            recommended_to_publish=True,
        )
        .select_related("author")
        .order_by("submitted_at")
    )
    my_submissions = TalkSubmission.objects.none()
    if request.user.is_authenticated:
        my_submissions = TalkSubmission.objects.filter(
            conference=conference,
            author=request.user,
        ).order_by("-submitted_at")
    return render(
        request,
        "app/conference_detail.html",
        {
            "conference": conference,
            "review_form": review_form,
            "reviews": reviews,
            "recommended_submissions": recommended_submissions,
            "my_submissions": my_submissions,
        },
    )


@login_required(login_url="login")
def submit_talk(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    if request.method == "POST":
        form = TalkSubmissionForm(request.POST)
        _style_form(form)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.conference = conference
            submission.author = request.user
            submission.save()
            messages.success(request, "Заявка на выступление отправлена.")
            return redirect("conference_detail", conference_id=conference.pk)
    else:
        form = TalkSubmissionForm()
        _style_form(form)

    return render(
        request,
        "app/talk_submission_form.html",
        {"conference": conference, "form": form, "is_editing": False},
    )


@login_required(login_url="login")
def edit_talk(request, submission_id):
    submission = get_object_or_404(
        TalkSubmission,
        pk=submission_id,
        author=request.user,
    )
    if request.method == "POST":
        form = TalkSubmissionForm(request.POST, instance=submission)
        _style_form(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка на выступление обновлена.")
            return redirect(
                "conference_detail",
                conference_id=submission.conference_id, # type: ignore
            )
    else:
        form = TalkSubmissionForm(instance=submission)
        _style_form(form)

    return render(
        request,
        "app/talk_submission_form.html",
        {
            "conference": submission.conference,
            "form": form,
            "is_editing": True,
            "submission": submission,
        },
    )


@login_required(login_url="login")
def delete_talk(request, submission_id):
    submission = get_object_or_404(
        TalkSubmission,
        pk=submission_id,
        author=request.user,
    )
    if request.method == "POST":
        conference_id = submission.conference_id # type: ignore
        submission.delete()
        messages.success(request, "Заявка на выступление удалена.")
        return redirect("conference_detail", conference_id=conference_id)

    return render(
        request,
        "app/talk_submission_confirm_delete.html",
        {"submission": submission},
    )
