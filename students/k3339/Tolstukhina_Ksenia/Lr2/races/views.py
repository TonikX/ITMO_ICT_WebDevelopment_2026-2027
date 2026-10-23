from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Race, User, Registration, Result, Auto
from .forms import UserRegistrationForm, CommentForm, UserProfileForm, ResultForm, AutoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "Доступ только для администраторов.")
        return redirect("races:race_list")


# Регистрация
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Регистрация успешна! Войдите в аккаунт")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "races/register.html", {"form": form})


# Просмотр профиля
@login_required
def profile(request):
    return render(request, "races/profile.html", {
        "profile_user": request.user,
        "auto_form": AutoForm(),
        "my_results": request.user.results
                  .filter(deleted_at__isnull=True)
                  .select_related("race", "auto")
                  .order_by("duration"),
    })


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("races:profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "races/profile_edit.html", {"form": form})


def public_profile(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    registrations = user_obj.registrations.select_related("race").all()
    results = user_obj.results.select_related("race", "auto").order_by("duration")
    comments = user_obj.comments.select_related("race").all()
    return render(request, "races/public_profile.html", {
        "profile_user": user_obj,
        "registrations": registrations,
        "results": results,
        "comments": comments,
    })


# Список всех участников
def participants(request):
    users = User.objects.filter(is_staff=False).order_by("last_name", "first_name")
    paginator = Paginator(users, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "races/participants.html", {"page_obj": page_obj})


# Регистрация на гонку
@login_required
def register_for_race(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == "POST":
        if Registration.objects.filter(user=request.user, race=race, deleted_at__isnull=True).exists():
            messages.warning(request, "Вы уже зарегистрированы на эту гонку.")
        else:
            Registration.objects.create(user=request.user, race=race)
            messages.success(request, f"Вы зарегистрированы на «{race.name}»!")
    return redirect("races:race_detail", pk=pk)


@login_required
def unregister_from_race(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user, deleted_at__isnull=True)
    race_pk = registration.race.pk
    registration.deleted_at = timezone.now()
    registration.save(update_fields=["deleted_at"])
    messages.success(request, "Регистрация удалена.")
    return redirect("races:race_detail", pk=race_pk)


# Написание комментов
@login_required
def add_comment(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.race = race
            comment.save()
            messages.success(request, "Комментарий добавлен.")
        else:
            messages.error(request, "Ошибка в форме комментария.")
    return redirect("races:race_detail", pk=pk)


# Таблица всех заездов и результатов
def results_table(request):
    races = Race.objects.prefetch_related(Prefetch("results", queryset=Result.objects.filter(deleted_at__isnull=True).select_related("user", "auto").order_by("duration"), to_attr="sorted_results"),).order_by("-date")
    return render(request, "races/results_table.html", {"races": races})


# Просмотр автогонок
class RaceListView(ListView):
    model = Race
    template_name = "races/race_list.html"
    context_object_name = "races"
    paginate_by = 9

    def get_queryset(self):
        qs = Race.objects.all().order_by("-date")
        q = self.request.GET.get("q")
        loc = self.request.GET.get("location")
        if q:
            qs = qs.filter(name__icontains=q)
        if loc:
            qs = qs.filter(location__icontains=loc)
        return qs


class RaceDetailView(DetailView):
    model = Race
    template_name = "races/race_detail.html"
    context_object_name = "race"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.object
        context["registrations"] = race.registrations.select_related("user").filter(deleted_at__isnull=True).all()
        context['results'] = race.results.select_related('user', 'auto').filter(deleted_at__isnull=True).all().order_by("duration")
        context['comments'] = race.comments.select_related('user').filter(deleted_at__isnull=True).all()
        context["comment_form"] = CommentForm(initial={"race_date": race.date})
        if self.request.user.is_authenticated:
            context["my_registration"] = race.registrations.filter(user=self.request.user, deleted_at__isnull=True).first()
        return context


class RaceUpdateView(StaffRequiredMixin, UpdateView):
    model = Race
    fields = ["name", "description", "date", "start_time", "end_time", "location"]
    template_name = "races/race_form.html"
    success_url = reverse_lazy("races:race_list")


# Создание гонки — только для админа
class RaceCreateView(StaffRequiredMixin, CreateView):
    model = Race
    fields = ["name", "description", "date", "start_time", "end_time", "location"]
    template_name = "races/race_form.html"
    success_url = reverse_lazy("races:race_list")

    def form_valid(self, form):
        messages.success(self.request, f"Гонка «{form.instance.name}» создана.")
        return super().form_valid(form)


# Добавление результата — только для админа
class ResultCreateView(StaffRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = "races/result_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.race = get_object_or_404(Race, pk=kwargs["race_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["race"] = self.race
        user_id = self.request.GET.get("user") or self.request.POST.get("user")
        if user_id:
            kwargs["user_id"] = user_id
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.request.GET.get("user")
        if user_id:
            initial["user"] = user_id
        return initial

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        auto = form.cleaned_data["auto"]

        if not Registration.objects.filter(user=user, race=self.race, deleted_at__isnull=True).exists():
            form.add_error("user", "Этот участник не зарегистрирован на гонку.")
            return self.form_invalid(form)

        if auto.owner_id != user.pk:
            form.add_error("auto", "Эта машина не принадлежит выбранному участнику.")
            return self.form_invalid(form)

        form.instance.race = self.race
        messages.success(self.request, "Результат добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("races:race_detail", kwargs={"pk": self.race.pk})


class AutoCreateView(LoginRequiredMixin, CreateView):
    model = Auto
    form_class = AutoForm
    template_name = "races/auto_form.html"
    success_url = reverse_lazy("races:profile")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Автомобиль {form.instance} добавлен.")
        return super().form_valid(form)