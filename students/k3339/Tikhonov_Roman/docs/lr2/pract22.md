# Практика 2.2. Представления и формы

## Выполненные задания методички

1. Связь «многие ко многим» между автомобилем, владением и владельцем
2. Представления: вывод владельцев функционально; автомобили — на основе классов
3. Формы: ввод владельца функционально; ввод, обновление и удаление автомобиля
   на основе классов

## Связь «многие ко многим»

Ассоциативная сущность `Ownership` содержит собственные атрибуты (даты начала и
окончания владения), поэтому связь оформлена по второму способу из методички —
через параметр `through`:

```python
class Owner(models.Model):
    cars = models.ManyToManyField("Car", through="Ownership")
```

Обращение к автомобилям владельца по связи: `owner.cars.all()`.

## Представления на основе функций

Список всех владельцев:

```python
def owner_list(request):
    context = {}
    context["dataset"] = Owner.objects.all()
    return render(request, "owners.html", context)
```

Форма ввода владельца (проверка `form.is_valid()` и сохранение):

```python
def owner_create(request):
    context = {}
    form = OwnerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/owners/")
    context["form"] = form
    return render(request, "owner_form.html", context)
```

Форма — `ModelForm`:

```python
class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["last_name", "first_name", "birth_date"]
```

## Представления на основе классов

Список автомобилей, автомобиль по id, создание, обновление и удаление —
generic-классы `ListView`, `DetailView`, `CreateView`, `UpdateView`,
`DeleteView`:

```python
class CarListView(ListView):
    model = Car
    template_name = "cars.html"


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = "/cars/"


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = "/cars/"


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = "/cars/"
```

Адресация:

```python
urlpatterns = [
    path("owners/", views.owner_list),
    path("owners/create/", views.owner_create),
    path("owner/<int:owner_id>/", views.owner_detail),
    path("cars/", views.CarListView.as_view()),
    path("cars/create/", views.CarCreateView.as_view()),
    path("cars/<int:pk>/", views.CarDetailView.as_view()),
    path("cars/<int:pk>/update/", views.CarUpdateView.as_view()),
    path("cars/<int:pk>/delete/", views.CarDeleteView.as_view()),
]
```

## Данные

Добавлены трёх владельцев (Кузнецов Дмитрий, Попова
Елена, Васильев Сергей) и три автомобиля (Hyundai Solaris, Kia Rio,
Volkswagen Polo):

```
Владельцев: 5 | Автомобилей: 7
```

## Результат


Отправка форм (POST с CSRF-токеном): обе формы сохраняют данные и выполняют
перенаправление на список. После отправки `/owners/create/` и `/cars/create/`
в списках появляются «Морозов Игорь» и «Skoda Octavia», форма обновления
автомобиля меняет его цвет.
