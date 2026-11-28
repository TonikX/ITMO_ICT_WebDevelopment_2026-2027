from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CommentForm, RacerForm, RegistrationForm, SignUpForm
from .models import Comment, Race, Racer, Registration, Result

RESULTS_ORDER = (F("position").asc(nulls_last=True), "registration__car_number")


class HomeView(TemplateView):
    """Табло победителей: призёры последних гонок, лучшие гонщики, ближайшие гонки."""

    template_name = "races/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished = []
        races = Race.objects.filter(heats__results__position__isnull=False).distinct().order_by("-date")[:6]
        for race in races:
            final = race.heats.filter(results__isnull=False).distinct().order_by("-number").first()
            podium = (
                final.results.filter(position__lte=3)
                .select_related("registration__racer__team")
                .order_by("position")
            )
            finished.append({"race": race, "heat": final, "podium": podium})
        context["finished"] = finished
        context["upcoming"] = Race.objects.filter(date__gte=timezone.localdate()).order_by("date")[:3]
        context["top_racers"] = (
            Racer.objects.select_related("team")
            .annotate(wins=Count("registrations__results", filter=Q(registrations__results__position=1)))
            .filter(wins__gt=0)
            .order_by("-wins", "full_name")[:5]
        )
        return context


class RaceListView(ListView):
    model = Race
    paginate_by = 6
    template_name = "races/race_list.html"

    def get_queryset(self):
        queryset = Race.objects.annotate(participants=Count("registrations"))
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(track__icontains=query))
        when = self.request.GET.get("when")
        today = timezone.localdate()
        if when == "upcoming":
            queryset = queryset.filter(date__gte=today).order_by("date")
        elif when == "past":
            queryset = queryset.filter(date__lt=today).order_by("-date")
        else:
            queryset = queryset.order_by("-date")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["when"] = self.request.GET.get("when", "")
        return context


class RaceDetailView(DetailView):
    """Гонка: участники (табло), таблица заездов и результатов, комментарии."""

    model = Race
    template_name = "races/race_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.object
        registrations = race.registrations.select_related("racer__team").order_by("car_number")
        results = Result.objects.select_related("registration__racer__team").order_by(*RESULTS_ORDER)
        heats = race.heats.prefetch_related(Prefetch("results", queryset=results)).order_by("number")
        comments = race.comments.select_related("author")
        context.update(
            registrations=registrations,
            heats=heats,
            comments=comments,
            rating=comments.aggregate(avg=Avg("rating"), count=Count("id")),
            comment_form=CommentForm(initial={"heat_date": race.date}),
            my_registration=None,
        )
        user = self.request.user
        if user.is_authenticated:
            context["my_registration"] = registrations.filter(racer__user=user).first()
        return context


class RacerListView(ListView):
    """Табло участников: поиск по ФИО и команде, фильтр по классу, пагинация."""

    model = Racer
    paginate_by = 8
    template_name = "races/racer_list.html"

    def get_queryset(self):
        queryset = Racer.objects.select_related("team").annotate(
            starts=Count("registrations", distinct=True),
            wins=Count(
                "registrations__results",
                filter=Q(registrations__results__position=1),
                distinct=True,
            ),
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(full_name__icontains=query) | Q(team__name__icontains=query))
        racer_class = self.request.GET.get("class", "")
        if racer_class in Racer.RacerClass.values:
            queryset = queryset.filter(racer_class=racer_class)
        return queryset.order_by("-wins", "full_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["selected_class"] = self.request.GET.get("class", "")
        context["classes"] = Racer.RacerClass.choices
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Аккаунт создан. Заполните профиль гонщика, чтобы регистрироваться на гонки.")
        return redirect("racer_profile")


def _safe_next(request, default):
    target = request.GET.get("next") or request.POST.get("next")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return default


class RacerProfileView(LoginRequiredMixin, UpdateView):
    """Создание или изменение своего профиля гонщика."""

    model = Racer
    form_class = RacerForm
    template_name = "races/racer_form.html"

    def get_object(self, queryset=None):
        try:
            return self.request.user.racer
        except Racer.DoesNotExist:
            return Racer(user=self.request.user, full_name=self.request.user.get_full_name())

    def form_valid(self, form):
        messages.success(self.request, "Профиль гонщика сохранён.")
        return super().form_valid(form)

    def get_success_url(self):
        return _safe_next(self.request, reverse("my_registrations"))


class MyRegistrationsView(LoginRequiredMixin, ListView):
    template_name = "races/my_registrations.html"
    context_object_name = "registrations"

    def get_queryset(self):
        return (
            Registration.objects.filter(racer__user=self.request.user)
            .select_related("race", "racer")
            .order_by("-race__date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["racer"] = Racer.objects.filter(user=self.request.user).select_related("team").first()
        return context


class RegistrationCreateView(LoginRequiredMixin, CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = "races/registration_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.race = get_object_or_404(Race, pk=kwargs["pk"])
        if not self.race.registration_is_open():
            messages.error(request, "Регистрация на эту гонку закрыта.")
            return redirect(self.race)
        self.racer = Racer.objects.filter(user=request.user).first()
        if self.racer is None:
            messages.info(request, "Сначала заполните профиль гонщика.")
            return redirect(f"{reverse('racer_profile')}?next={request.path}")
        if Registration.objects.filter(race=self.race, racer=self.racer).exists():
            messages.info(request, "Вы уже зарегистрированы на эту гонку.")
            return redirect(self.race)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        taken = set(self.race.registrations.values_list("car_number", flat=True))
        free_number = next(n for n in range(1, 1000) if n not in taken)
        last = self.racer.registrations.order_by("-created_at").first()
        return {"car_number": free_number, "car_description": last.car_description if last else ""}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(race=self.race, racer=self.racer)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race"] = self.race
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Вы зарегистрированы на гонку «{self.race.title}».")
        return super().form_valid(form)

    def get_success_url(self):
        return self.race.get_absolute_url()


class OwnRegistrationMixin(LoginRequiredMixin):
    """Только свои регистрации и только пока гонка не прошла."""

    model = Registration

    def get_queryset(self):
        return Registration.objects.filter(racer__user=self.request.user).select_related("race", "racer")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        registration = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not registration.can_be_changed():
            messages.error(request, "Гонка уже прошла или по ней есть результаты: регистрацию изменить нельзя.")
            return redirect("my_registrations")
        return super().dispatch(request, *args, **kwargs)


class RegistrationUpdateView(OwnRegistrationMixin, UpdateView):
    form_class = RegistrationForm
    template_name = "races/registration_form.html"
    success_url = reverse_lazy("my_registrations")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(race=self.object.race, racer=self.object.racer)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race"] = self.object.race
        return context

    def form_valid(self, form):
        messages.success(self.request, "Регистрация изменена.")
        return super().form_valid(form)


class RegistrationDeleteView(OwnRegistrationMixin, DeleteView):
    template_name = "races/registration_confirm_delete.html"
    success_url = reverse_lazy("my_registrations")

    def form_valid(self, form):
        messages.success(self.request, "Регистрация отменена.")
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Отзыв к гонке: дата заезда, текст, тип, рейтинг 1–10, автор."""

    model = Comment
    form_class = CommentForm
    template_name = "races/comment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.race = get_object_or_404(Race, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {"heat_date": self.race.date}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race"] = self.race
        return context

    def form_valid(self, form):
        form.instance.race = self.race
        form.instance.author = self.request.user
        messages.success(self.request, "Спасибо, комментарий добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return f"{self.race.get_absolute_url()}#comments"
