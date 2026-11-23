from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Дополнительные сведения', {'fields': (
        'birth_date', 'passport_number', 'home_address', 'nationality')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Дополнительные сведения', {'fields': (
        'first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality')}),)
