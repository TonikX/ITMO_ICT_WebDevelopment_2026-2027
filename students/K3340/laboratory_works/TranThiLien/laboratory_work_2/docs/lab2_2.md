# Практическая работа 2.2

## M2M через ассоциативную сущность. FBV, CBV, формы

Проект: `django_project_tran`, приложение: `project_first_app`.

---

## 1. Связь «многие ко многим» через промежуточную модель

У владения есть собственные атрибуты — дата начала и дата окончания, поэтому связь
автомобиля и владельца оформлена через ассоциативную сущность `Ownership` и параметр `through`:

```python
class Car(models.Model):
    ...
    owners = models.ManyToManyField(CarOwner, through='Ownership',
                                    related_name='cars', verbose_name='Владельцы')


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name='ownerships')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='ownerships')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата конца', null=True, blank=True)
```

Навигация доступна в обе стороны: `car.owners.all()` и `owner.cars.all()`.
Новое владение создаётся явно, с датами: `Ownership.objects.create(owner=..., car=..., start_date=...)`.

## 2. Формы

**forms.py**:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Car, CarOwner


class CarOwnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ('username', 'last_name', 'first_name', 'birth_date',
                  'passport_number', 'home_address', 'nationality')
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model', 'color']
```

Владелец является пользователем (практика 2.3), поэтому форма владельца построена
на `UserCreationForm` — она добавляет поля пароля и хэширует его при сохранении.

## 3. FBV — вывод и создание владельцев

```python
from django.shortcuts import redirect, render
from .forms import CarOwnerForm
from .models import CarOwner


def owner_list(request):
    """Вывод всех владельцев (функционально)."""
    context = {'owners': CarOwner.objects.filter(is_superuser=False).order_by('last_name')}
    return render(request, 'owner_list.html', context)


def owner_create(request):
    """Форма ввода владельца (функционально)."""
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'owner_form.html', {'form': form})
```

Шаблон формы выводит поля вручную, с сообщениями об ошибках:

```html
<form method="post">
  {% csrf_token %}
  {% for field in form %}
    <label for="{{ field.id_for_label }}">{{ field.label }}</label>
    {{ field }}
    {% for error in field.errors %}<div class="text-danger">{{ error }}</div>{% endfor %}
  {% endfor %}
  <button type="submit">Сохранить</button>
</form>
```

## 4. CBV — CRUD автомобилей

```python
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import CarForm
from .models import Car


class CarListView(ListView):
    model = Car
    template_name = 'project_first_app/car_list.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'project_first_app/car_detail.html'


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'project_first_app/car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'project_first_app/car_form.html'
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'project_first_app/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
```

Страница автомобиля (`car_detail.html`) показывает историю владения через `object.ownerships.all`.

## 5. Шаблоны

Все шаблоны наследуют `base.html` с навигацией и Bootstrap 5:

| Шаблон | Представление |
|--------|---------------|
| `base.html` | базовый шаблон с меню |
| `owner.html` | `owner_detail` (практика 2.1) |
| `owner_list.html` | `owner_list` |
| `owner_form.html` | `owner_create` |
| `project_first_app/car_list.html` | `CarListView` |
| `project_first_app/car_detail.html` | `CarDetailView` |
| `project_first_app/car_form.html` | `CarCreateView`, `CarUpdateView` |
| `project_first_app/car_confirm_delete.html` | `CarDeleteView` |

## 6. URL

```python
urlpatterns = [
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),

    path('owners/', views.owner_list, name='owner_list'),
    path('owners/create/', views.owner_create, name='owner_create'),

    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/<int:pk>/update/', views.CarUpdateView.as_view(), name='car_update'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]
```

## Результат

| Адрес | Что делает | Тип |
|-------|------------|-----|
| `/owners/` | список всех владельцев | FBV |
| `/owners/create/` | форма ввода владельца | FBV |
| `/cars/` | список всех автомобилей | CBV `ListView` |
| `/cars/<id>/` | автомобиль по id и история владения | CBV `DetailView` |
| `/cars/create/` | создание автомобиля | CBV `CreateView` |
| `/cars/<id>/update/` | обновление автомобиля | CBV `UpdateView` |
| `/cars/<id>/delete/` | удаление с подтверждением | CBV `DeleteView` |

Через формы добавлены ещё минимум три владельца и три автомобиля.
