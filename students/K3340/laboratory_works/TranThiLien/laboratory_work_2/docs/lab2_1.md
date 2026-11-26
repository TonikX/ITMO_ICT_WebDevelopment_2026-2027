# Практическая работа 2.1

## Установка Django. Реализация первого приложения

Проект: `django_project_tran`, приложение: `project_first_app`.

---

## 1. Установка

```bash
cd laboratory_work_2
py -m venv tutorial-env
tutorial-env\Scripts\activate.bat
pip install django
django-admin startproject django_project_tran
cd django_project_tran
python manage.py startapp project_first_app
```

## 2. Настройка settings.py

Приложение подключено в `INSTALLED_APPS`, выбран русский язык и московское время:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "project_first_app",
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"

# Своя модель пользователя (практика 2.3) задана ДО первой миграции
AUTH_USER_MODEL = 'project_first_app.CarOwner'
```

`AUTH_USER_MODEL` нельзя безболезненно изменить после первой миграции, поэтому модель
владельца сразу объявлена как пользователь (подробнее — в [практической работе 2.3](lab2_3.md)).

## 3. Модель данных

Модель об автовладельцах соответствует рисунку 2 из задания. Таблицы и атрибуты названы латиницей.

| Модель | Поля | Связи |
|--------|------|-------|
| `CarOwner` (Автовладелец) | `last_name`, `first_name`, `birth_date` | — |
| `Car` (Автомобиль) | `license_plate`, `brand`, `model`, `color` | M:N с `CarOwner` через `Ownership` |
| `Ownership` (Владение) | `start_date`, `end_date` | FK `owner`, FK `car` |
| `DriverLicense` (Водительское удостоверение) | `number`, `type` (choices), `issue_date` | FK `owner` |

```python
class Car(models.Model):
    license_plate = models.CharField('Гос. номер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(CarOwner, through='Ownership',
                                    related_name='cars', verbose_name='Владельцы')


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name='ownerships')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='ownerships')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата конца', null=True, blank=True)


class DriverLicense(models.Model):
    TYPES = (
        ('A', 'A — мотоциклы'),
        ('B', 'B — легковые автомобили'),
        ('C', 'C — грузовые автомобили'),
        ('D', 'D — автобусы'),
    )
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name='licenses')
    number = models.CharField('Номер удостоверения', max_length=10, unique=True)
    type = models.CharField('Тип', max_length=1, choices=TYPES)
    issue_date = models.DateField('Дата выдачи')
```

- `type` — поле выбора (`choices`): в БД хранится буква, пользователю показывается описание.
- `Ownership` — ассоциативная сущность со своими атрибутами (даты владения).

## 4. Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

```text
Migrations for 'project_first_app':
  project_first_app/migrations/0001_initial.py
    + Create model Car
    + Create model CarOwner
    + Create model DriverLicense
    + Create model Ownership
    + Add field owners to car
```

## 5. Админ-панель

Все таблицы зарегистрированы в `admin.py`. Владения и удостоверения редактируются
прямо на странице владельца и автомобиля (inline):

```python
class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model', 'color')
    inlines = [OwnershipInline]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'owner', 'type', 'issue_date')
```

```bash
python manage.py createsuperuser
python manage.py runserver
```

### Данные (практическое задание 3)

Добавлены 2 владельца и 4 автомобиля. Каждый владелец связан минимум с тремя
автомобилями, периоды владения одной машиной не пересекаются: машина переходит
к следующему владельцу на следующий день после окончания предыдущего владения.

| Автомобиль | Анна Смирнова | Борис Петров |
|------------|---------------|--------------|
| Lada Vesta | 10.01.2015 – 01.05.2018 | 02.05.2018 – н. в. |
| Kia Rio | 01.06.2018 – 01.02.2021 | 02.02.2021 – 01.09.2023 |
| Volkswagen Polo | 01.03.2021 – н. в. | — |
| Skoda Octavia | 02.04.2020 – н. в. | 01.04.2016 – 01.04.2020 |

Данные можно ввести через `/admin/` или командой:

```bash
python manage.py seed_practice2
```

## 6. Первое представление

**views.py** — информация о владельце по идентификатору:

```python
from django.shortcuts import get_object_or_404, render
from .models import CarOwner


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})
```

**templates/owner.html** (фрагмент) — поля владельца, удостоверения и автомобили:

```html
<h1>{{ owner.last_name }} {{ owner.first_name }}</h1>
<p>Дата рождения: {{ owner.birth_date|date:"d.m.Y" }}</p>

<h2>Водительские удостоверения</h2>
{% for license in owner.licenses.all %}
  <p>{{ license.number }} — {{ license.get_type_display }}</p>
{% endfor %}

<h2>Автомобили</h2>
{% for own in owner.ownerships.all %}
  <p>{{ own.car }}: {{ own.start_date }} — {{ own.end_date|default:"по настоящее время" }}</p>
{% endfor %}
```

## 7. Адресация (URLs)

**project_first_app/urls.py**:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
]
```

**django_project_tran/urls.py**:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project_first_app.urls')),
]
```

## Результат

- `/admin/` — 4 таблицы: Автовладельцы, Автомобили, Владения, Водительские удостоверения.
- `/owner/1/` — страница с информацией о первом владельце, его удостоверении и автомобилях.
