"""Регистрация учебных моделей и расширенного пользователя."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, DriverLicense, Ownership, User


@admin.register(User)
class OwnerAdmin(UserAdmin):
    """Добавляет атрибуты владельца в формы администратора."""

    fieldsets = UserAdmin.fieldsets + (
        (
            "Автовладелец",
            {"fields": ("birth_date", "passport_number", "address", "nationality")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Автовладелец",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_date",
                    "passport_number",
                    "address",
                    "nationality",
                )
            },
        ),
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
