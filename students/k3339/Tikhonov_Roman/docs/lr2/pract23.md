# Практика 2.3. Расширение пользовательской модели

## Задание

Сделать владельца автомобиля пользователем и расширить модель пользователя
атрибутами: номер паспорта, домашний адрес, национальность. Отобразить новые
поля в Django Admin, отредактировать предыдущие работы под пользователей,
реализовать интерфейс создания пользователя.

Использован рекомендуемый в методичке способ — наследование `AbstractUser`
(способ 4): процесс аутентификации Django не меняется, дополнительные атрибуты
хранятся в самой модели пользователя.

## Модель пользователя

```python
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=12, blank=True)
    home_address = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    cars = models.ManyToManyField("Car", through="Ownership")

    def __str__(self):
        return self.get_full_name() or self.username
```

В `settings.py` объявлена модель пользователя, внешние ключи `Ownership` и
`DriverLicense` ссылаются на неё через `settings.AUTH_USER_MODEL`; отдельная
модель `Owner` удалена:


```python
class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    ...
```

Модель пользователя меняется в начале проекта, поэтому миграции сформированы
заново единым файлом `0001_initial.py` (создание Car, User, DriverLicense,
Ownership), база пересоздана.

## Отображение в Django Admin

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Car, DriverLicense, Ownership, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Дополнительные сведения", {
            "fields": ("birth_date", "passport_number", "home_address", "nationality"),
        }),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Дополнительные сведения", {
            "fields": ("birth_date", "passport_number", "home_address", "nationality"),
        }),
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
```

## Интерфейс создания пользователя

Форма наследуется от `UserCreationForm` — корректно обрабатывает пароль
(поля `password1`/`password2` с валидацией):

```python
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
        ]
```

Представления этапов 2.1–2.2 переведены с модели `Owner` на модель `User`
(список `/owners/`, карточка `/owner/<id>/`, создание `/owners/create/`).

## Результат

Создание пользователя через клиентскую форму: после отправки формы
`/owners/create/` выполняется перенаправление на список

В админ-панели у пользователя появился блок «Дополнительные сведения» с полями
Birth date, Passport number, Home address, Nationality.
