from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .forms import RegistrationForm

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('tour_list')
    return render(request, 'form.html', {'form':form, 'title':'Регистрация', 'button':'Создать аккаунт'})

@require_POST
def sign_out(request):
    logout(request)
    return redirect('tour_list')
