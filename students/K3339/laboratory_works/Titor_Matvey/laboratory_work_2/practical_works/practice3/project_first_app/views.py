
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import UserRegisterForm
from .models import Car, User

def register(request):
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
    users = User.objects.all().order_by('last_name', 'username')
    return render(request, 'people_list.html', {'users': users})

def owner(request, pk):
    person = get_object_or_404(User, pk=pk)
    context = {
        'owner': person,
        'ownerships': person.ownerships.select_related('car'),
    }
    return render(request, 'owner.html', context)

class CarListView(ListView):

    model = Car
    template_name = 'car_list.html'
    ordering = ('brand', 'model')
