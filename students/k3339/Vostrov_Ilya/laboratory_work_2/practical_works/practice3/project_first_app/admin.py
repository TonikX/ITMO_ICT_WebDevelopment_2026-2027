"""Регистрация моделей в админке (Практика 3).

Собственный пользователь (AbstractUser) регистрируется с расширенным
UserAdmin, чтобы дополнительные поля (паспорт, адрес, национальность)
были видны и редактируемы в панели администратора.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, Ownership, User


class CustomUserAdmin(UserAdmin):
    """UserAdmin + новые поля владельца автомобиля."""

    fieldsets = UserAdmin.fieldsets + (
        ('Данные владельца', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные владельца', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )
    list_display = ('username', 'last_name', 'first_name', 'passport_number', 'nationality', 'is_staff')
    search_fields = ('username', 'last_name', 'first_name', 'passport_number', 'nationality')


# Стандартный UserAdmin уже регистрирует модель пользователя из AUTH_USER_MODEL
# (через get_user_model) — переопределяем его нашей версией.
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'color', 'state_number')
    search_fields = ('brand', 'model', 'state_number')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')
    search_fields = ('owner__username', 'car__state_number')
