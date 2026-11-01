"""Тонкий слой: параметры запроса -> forms/services, права -> permissions, ответ -> шаблон."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from . import services
from .forms import (
    ConferenceFilter, ConferenceForm, ParticipantFilter, ParticipationForm, RegisterForm, ResultForm, ReviewForm,
)
from .models import Conference, Participation, Review
from .permissions import OwnerOnlyMixin, StaffRequiredMixin, reviews_manageable_by

FORM_TEMPLATE = "conferences/form.html"
DELETE_TEMPLATE = "conferences/confirm_delete.html"


class RegisterView(FormView):
    template_name = "conferences/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("conference-list")

    def form_valid(self, form):
        login(self.request, form.save())
        messages.success(self.request, "Регистрация прошла успешно.")
        return super().form_valid(form)


class FilteredListView(ListView):
    """Список, который фильтруется формой по GET-параметрам; ссылки пагинации сохраняют фильтры."""

    filter_form = None

    def get_queryset(self):
        form = self.filter_form(self.request.GET)
        form.is_valid()  # ошибочные параметры отбрасываются, остальные остаются в cleaned_data
        return self.apply_filters(form.cleaned_data)

    def apply_filters(self, filters):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filters"] = self.request.GET
        ctx["query"] = services.querystring_without_page(self.request.GET)
        return ctx


class ConferenceListView(FilteredListView):
    template_name = "conferences/conference_list.html"
    context_object_name = "conferences"
    paginate_by = 5
    filter_form = ConferenceFilter

    def apply_filters(self, filters):
        return services.search_conferences(filters)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(services.filter_options())
        return ctx


class ParticipantsView(FilteredListView):
    """Таблицы участников по конференциям: страница — несколько конференций, у каждой своя таблица."""

    template_name = "conferences/participants.html"
    paginate_by = 3
    filter_form = ParticipantFilter

    def apply_filters(self, filters):
        self.participations = services.filter_participations(filters)
        return services.conferences_with_participants(self.participations)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["groups"] = services.group_by_conference(ctx["page_obj"].object_list, self.participations)
        ctx["all_conferences"] = Conference.objects.all()
        ctx["results"] = Participation.Result.choices
        return ctx


class ConferenceDetailView(DetailView):
    model = Conference
    template_name = "conferences/conference_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        conference = self.object
        reviews = conference.reviews.select_related("author")
        ctx["reviews"] = Paginator(reviews, 5).get_page(self.request.GET.get("page"))
        ctx["avg_rating"] = services.average_rating(conference)
        ctx["my_participation"] = services.get_participation(conference, self.request.user)
        return ctx


class ConferenceCreateView(StaffRequiredMixin, CreateView):
    model = Conference
    form_class = ConferenceForm
    template_name = FORM_TEMPLATE
    extra_context = {"title": "Новая конференция"}


class ConferenceUpdateView(StaffRequiredMixin, UpdateView):
    model = Conference
    form_class = ConferenceForm
    template_name = FORM_TEMPLATE
    extra_context = {"title": "Редактирование конференции"}


class ConferenceDeleteView(StaffRequiredMixin, DeleteView):
    model = Conference
    template_name = DELETE_TEMPLATE
    success_url = reverse_lazy("conference-list")
    extra_context = {"warning": "Вместе с конференцией удалятся все её регистрации и отзывы."}


class ForConferenceMixin(LoginRequiredMixin):
    """Форма для конференции из адреса; заголовок собирается из `title_prefix`."""

    template_name = FORM_TEMPLATE
    title_prefix = ""

    def dispatch(self, request, *args, **kwargs):
        self.conference = get_object_or_404(Conference, pk=kwargs["conference_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"{self.title_prefix} «{self.conference.title}»"
        return ctx


class ParticipationCreateView(ForConferenceMixin, CreateView):
    form_class = ParticipationForm
    title_prefix = "Регистрация на"

    def get(self, request, *args, **kwargs):
        if services.get_participation(self.conference, request.user):
            messages.info(request, "Вы уже зарегистрированы на эту конференцию.")
            return redirect(self.conference)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        _, created = services.register_author(self.conference, self.request.user, **form.cleaned_data)
        if created:
            messages.success(self.request, "Вы зарегистрированы как автор доклада.")
        else:
            messages.info(self.request, "Вы уже зарегистрированы на эту конференцию.")
        return redirect("my-participations")


class ReviewCreateView(ForConferenceMixin, CreateView):
    form_class = ReviewForm
    title_prefix = "Отзыв о"

    def form_valid(self, form):
        form.instance.conference = self.conference
        form.instance.author = self.request.user
        messages.success(self.request, "Отзыв добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.conference.get_absolute_url()


class MyParticipationsView(LoginRequiredMixin, ListView):
    template_name = "conferences/my_participations.html"
    context_object_name = "participations"
    paginate_by = 10

    def get_queryset(self):
        return Participation.objects.filter(user=self.request.user).select_related("conference")


class ParticipationUpdateView(OwnerOnlyMixin, UpdateView):
    model = Participation
    form_class = ParticipationForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("my-participations")
    extra_context = {"title": "Редактирование регистрации"}


class ParticipationDeleteView(OwnerOnlyMixin, DeleteView):
    model = Participation
    template_name = DELETE_TEMPLATE
    success_url = reverse_lazy("my-participations")


class ParticipationResultView(StaffRequiredMixin, UpdateView):
    """Администратор указывает результат выступления прямо в клиентской части."""

    model = Participation
    form_class = ResultForm
    template_name = FORM_TEMPLATE
    extra_context = {"title": "Результат выступления"}

    def get_success_url(self):
        return reverse("participants") + f"?conference={self.object.conference_id}"


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    template_name = DELETE_TEMPLATE

    def get_queryset(self):
        return reviews_manageable_by(self.request.user, Review.objects.all())

    def get_success_url(self):
        return self.object.conference.get_absolute_url()
