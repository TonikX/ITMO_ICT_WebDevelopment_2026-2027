from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegistrationForm


def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        messages.success(request, 'Аккаунт создан. Теперь можно бронировать рейсы.')
        return redirect('flight_list')
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация', 'submit': 'Создать аккаунт'})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён.')
        return redirect('profile')
    return render(request, 'form.html', {'form': form, 'title': 'Мой профиль', 'submit': 'Сохранить'})
