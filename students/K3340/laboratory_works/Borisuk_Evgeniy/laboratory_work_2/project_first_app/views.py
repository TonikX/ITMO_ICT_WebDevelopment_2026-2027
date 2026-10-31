"""FBV владельцев и CBV автомобилей для практических заданий."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CarForm, OwnerForm
from .models import Car, User


def require_staff(request: HttpRequest) -> None:
    """Ограничивает доступ к персональным данным владельцев."""
    if not request.user.is_staff:
        raise PermissionDenied


@login_required
def owner_list(request: HttpRequest) -> HttpResponse:
    """Выводит всех владельцев функциональным представлением."""
    require_staff(request)
    return render(request, "owners.html", {"owners": User.objects.order_by("pk")})


@login_required
def owner_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Выводит владельца и связанные автомобили по идентификатору."""
    require_staff(request)
    owner = get_object_or_404(User, pk=pk)
    return render(request, "owner.html", {"owner": owner})


@login_required
def owner_create(request: HttpRequest) -> HttpResponse:
    """Создаёт пользователя-автовладельца через FBV."""
    require_staff(request)
    form = OwnerForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        owner = form.save()
        return redirect("practice:owner_detail", pk=owner.pk)
    return render(request, "form.html", {"form": form, "title": "Новый автовладелец"})


class StaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Защищает учебные операции администратора."""

    def test_func(self) -> bool:
        return self.request.user.is_staff


class CarList(StaffMixin, ListView):
    """Список автомобилей через CBV."""

    model = Car
    template_name = "cars.html"


class CarDetail(StaffMixin, DetailView):
    """Карточка автомобиля через CBV."""

    model = Car
    template_name = "car.html"


class CarCreate(StaffMixin, CreateView):
    """Создание автомобиля через CBV."""

    model = Car
    form_class = CarForm
    template_name = "form.html"
    extra_context = {"title": "Новый автомобиль"}
    success_url = reverse_lazy("practice:car_list")


class CarUpdate(StaffMixin, UpdateView):
    """Обновление автомобиля через CBV."""

    model = Car
    form_class = CarForm
    template_name = "form.html"
    extra_context = {"title": "Редактировать автомобиль"}
    success_url = reverse_lazy("practice:car_list")


class CarDelete(StaffMixin, DeleteView):
    """Удаление автомобиля через CBV с подтверждением."""

    model = Car
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("practice:car_list")
