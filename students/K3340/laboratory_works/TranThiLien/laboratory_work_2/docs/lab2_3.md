# Практическая работа 2.3

## Расширение пользователя

Проект: `django_project_tran`, приложение: `project_first_app`.

---

## 1. Выбор способа расширения

| Способ | Новые поля в БД | Подходит ли |
|--------|-----------------|-------------|
| Proxy-модель | нет | нет — нужны новые поля |
| OneToOneField (профиль) | да, отдельная таблица | возможно, но данные разнесены по двум таблицам |
| AbstractBaseUser | да, замена таблицы | избыточно — стандартная аутентификация устраивает |
| **AbstractUser** | да, расширение таблицы users | **выбран**: стандартный вход по логину и паролю + свои поля |

## 2. Модель пользователя

«Владелец автомобиля» сделан пользователем. Поля `first_name`, `last_name`,
`username`, `password` уже есть в `AbstractUser`, добавлены атрибуты владельца:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    home_address = models.CharField('Домашний адрес', max_length=255, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    def __str__(self):
        full_name = f'{self.last_name} {self.first_name}'.strip()
        return full_name or self.username
```

## 3. Подключение в settings.py

```python
AUTH_USER_MODEL = 'project_first_app.CarOwner'
```

Настройка задана до первой миграции — иначе пришлось бы пересоздавать связанные таблицы.

## 4. Ссылки на модель пользователя

Остальные модели ссылаются на `CarOwner` из того же приложения. В коде вне приложения
пользователь берётся через `settings.AUTH_USER_MODEL` (в `ForeignKey`) или `get_user_model()`.

```python
class DriverLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name='licenses')
    ...
```

## 5. Новые поля в Django Admin

`CarOwnerAdmin` наследует `UserAdmin`, чтобы сохранить стандартные разделы пользователя
(пароль, права, даты), и добавляет раздел с данными владельца:

```python
from django.contrib.auth.admin import UserAdmin


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'passport_number',
                    'nationality', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Данные автовладельца', {
            'fields': ('birth_date', 'passport_number', 'home_address', 'nationality'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные автовладельца', {
            'fields': ('first_name', 'last_name', 'birth_date',
                       'passport_number', 'home_address', 'nationality'),
        }),
    )
    inlines = [DriverLicenseInline, OwnershipInline]
```

## 6. Вывод информации о пользователях

Код из практик 2.1 и 2.2 изменён так, чтобы выводились новые поля.

`owner_list.html` — таблица пользователей-владельцев:

```html
{% for owner in owners %}
  <tr>
    <td><a href="{% url 'owner_detail' owner.id %}">{{ owner.last_name }} {{ owner.first_name }}</a></td>
    <td>{{ owner.birth_date|date:"d.m.Y"|default:"—" }}</td>
    <td>{{ owner.passport_number|default:"—" }}</td>
    <td>{{ owner.home_address|default:"—" }}</td>
    <td>{{ owner.nationality|default:"—" }}</td>
    <td>{{ owner.cars.count }}</td>
  </tr>
{% endfor %}
```

`owner.html` — карточка владельца с логином, паспортом, адресом, национальностью,
удостоверениями и автомобилями.

## 7. Интерфейс создания пользователя

Форма `CarOwnerForm` наследует `UserCreationForm` и содержит новые атрибуты:

```python
class CarOwnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ('username', 'last_name', 'first_name', 'birth_date',
                  'passport_number', 'home_address', 'nationality')
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}
```

Страница `/owners/create/`: логин, фамилия, имя, дата рождения, номер паспорта,
домашний адрес, национальность, пароль и подтверждение пароля. Пароль сохраняется
в виде хэша.

## Результат

- `/admin/` — у автовладельца раздел «Данные автовладельца» с новыми полями;
  при создании пользователя в админке они тоже заполняются.
- `/owners/` — список пользователей-владельцев с паспортом, адресом и национальностью.
- `/owner/<id>/` — полная информация о пользователе.
- `/owners/create/` — создание пользователя с новыми атрибутами.
