"""Представления приложения "Автовладельцы" (Практика 3).

- register: форма создания учётной записи с новыми атрибутами;
- people_list: вывод сведений о пользователях (владельцах) — "прежний код",
  теперь показывает паспорт/адрес/национальность;
- owner: страница одного владельца-пользователя и его автомобилей;
- CarListView: список автомобилей (CBV), для полноты.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import UserRegisterForm
from .models import Car, User


def register(request):
    """Создание учётной записи пользователя-владельца."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация завершена. Теперь можно войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def people_list(request):
    """Все владельцы (пользователи) с расширенными данными."""
    users = User.objects.all().order_by('last_name', 'username')
    return render(request, 'people_list.html', {'users': users})


def owner(request, pk):
    """Страница владельца-пользователя и его автомобилей."""
    person = get_object_or_404(User, pk=pk)
    context = {
        'owner': person,
        'ownerships': person.ownerships.select_related('car'),
    }
    return render(request, 'owner.html', context)


class CarListView(ListView):
    """Список автомобилей (CBV)."""

    model = Car
    template_name = 'car_list.html'
    ordering = ('brand', 'model')
