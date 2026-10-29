from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ParticipationForm, ReviewForm, SignUpForm
from .models import Conference, Participation, Review, Topic


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("conference_list")


class ConferenceListView(ListView):
    model = Conference
    paginate_by = 4

    def get_queryset(self):
        queryset = Conference.objects.prefetch_related("topics")
        q = self.request.GET.get("q", "")
        topic = self.request.GET.get("topic", "")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(venue__icontains=q))
        if topic.isdigit():
            queryset = queryset.filter(topics__id=topic)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = Topic.objects.all()
        return context


class ConferenceDetailView(DetailView):
    model = Conference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conference = self.object
        context["reviews"] = conference.reviews.select_related("user")
        context["avg_rating"] = conference.reviews.aggregate(Avg("rating"))["rating__avg"]
        if self.request.user.is_authenticated:
            context["my_participation"] = conference.participations.filter(
                user=self.request.user).first()
        return context


class ParticipationCreateView(LoginRequiredMixin, CreateView):
    form_class = ParticipationForm
    template_name = "conferences/participation_form.html"
    success_url = reverse_lazy("my_participations")

    def dispatch(self, request, *args, **kwargs):
        self.conference = get_object_or_404(Conference, pk=kwargs["pk"])
        if request.user.is_authenticated and self.conference.participations.filter(
                user=request.user).exists():
            messages.warning(request, "Вы уже зарегистрированы на эту конференцию.")
            return redirect("my_participations")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conference"] = self.conference
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.conference = self.conference
        messages.success(self.request, "Вы зарегистрированы как автор доклада.")
        return super().form_valid(form)


class MyParticipationListView(LoginRequiredMixin, ListView):
    template_name = "conferences/my_participations.html"

    def get_queryset(self):
        return Participation.objects.filter(user=self.request.user).select_related("conference")


class ParticipationUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ParticipationForm
    success_url = reverse_lazy("my_participations")

    def get_queryset(self):
        return Participation.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conference"] = self.object.conference
        return context


class ParticipationDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy("my_participations")

    def get_queryset(self):
        return Participation.objects.filter(user=self.request.user)


class ParticipantListView(ListView):
    template_name = "conferences/participant_list.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = Participation.objects.select_related("user", "conference")
        q = self.request.GET.get("q", "")
        conference = self.request.GET.get("conference", "")
        result = self.request.GET.get("result", "")
        if q:
            queryset = queryset.filter(
                Q(user__last_name__icontains=q) | Q(user__first_name__icontains=q)
                | Q(talk_title__icontains=q))
        if conference.isdigit():
            queryset = queryset.filter(conference_id=conference)
        if result:
            queryset = queryset.filter(result=result)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conferences"] = Conference.objects.all()
        context["result_choices"] = Participation.RESULT_CHOICES
        return context


@login_required
@require_POST
def set_result(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    participation = get_object_or_404(Participation, pk=pk)
    result = request.POST.get("result")
    if result in dict(Participation.RESULT_CHOICES):
        participation.result = result
        participation.save()
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("participant_list")


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    template_name = "conferences/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.conference = get_object_or_404(Conference, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conference"] = self.conference
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.conference = self.conference
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("conference_detail", args=[self.conference.pk])


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review

    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("conference_detail", args=[self.object.conference.pk])
