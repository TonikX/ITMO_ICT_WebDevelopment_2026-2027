# Практика 2.1. Django Web framework. Установка. Реализация первого приложения

## Выполненные задания методички

1. Установка Django Web framework
2. Создание модели Django (автовладельцы, по схеме из методички)
3. Создание админ-панели и наполнение данными
4. Создание контроллеров для обработки данных
5. Работа с адресацией

## Установка

Виртуальное окружение и установка фреймворка:

```
> py -m venv .venv
> .venv\Scripts\activate
> pip install django
> pip freeze
asgiref==3.13.0
Django==5.2
sqlparse==0.6.1
tzdata==2026.6
```

Создание проекта `django_project_tikhonov` и приложения `project_first_app`
(форматы имён — из методички):

```
> django-admin startproject django_project_tikhonov
> python manage.py startapp project_first_app
```

Приложение подключено в `INSTALLED_APPS`, для шаблонов добавлена папка
`templates` (настройка `DIRS`).

## Модель данных

По рисунку 2 методички: четыре таблицы, ассоциативная сущность «Владение»,
связь «многие ко многим» между владельцем и автомобилем оформлена через неё.
Все имена — на латинице.

```python
from django.db import models


class Owner(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    cars = models.ManyToManyField("Car", through="Ownership")

    def __str__(self):
        return "{} {}" .format(self.last_name, self.first_name)


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.brand, self.model)


class Ownership(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.owner, self.car)


class DriverLicense(models.Model):
    LICENSE_TYPES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("M", "M"),
    ]
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=1, choices=LICENSE_TYPES)
    issue_date = models.DateField()

    def __str__(self):
        return "{} ({})".format(self.license_number, self.license_type)
```


## Админ-панель

Все четыре модели зарегистрированы в `admin.py`:

```python
from django.contrib import admin

from .models import Car, DriverLicense, Ownership, Owner

admin.site.register(Owner)
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
```

Создание суперпользователя: `python manage.py createsuperuser`.


```
Иванов Пётр | cars: Ford Focus, Toyota Camry, Lada Vesta
Смирнова Анна | cars: Ford Focus, Toyota Camry, BMW X5
Владений: 6 | Удостоверений: 3
```

## Контроллер и адресация

Представление «владелец по id» по образцу из официальной документации
(обработка отсутствующей записи через `Http404`):

```python
from django.http import Http404
from django.shortcuts import render

from .models import Owner


def owner_detail(request, owner_id):
    try:
        owner = Owner.objects.get(pk=owner_id)
    except Owner.DoesNotExist:
        raise Http404("Owner does not exist")
    return render(request, "owner.html", {"owner": owner})
```

Шаблон `templates/owner.html` выводит поля модели. Файл адрес приложения
подключён к проекту через `include`:

```python
from django.urls import path

from . import views

urlpatterns = [
    path("owner/<int:owner_id>/", views.owner_detail),
]
```

## Результат

В админ-панели зарегистрированы модели Owners, Cars, Ownership, Driver licenses.
