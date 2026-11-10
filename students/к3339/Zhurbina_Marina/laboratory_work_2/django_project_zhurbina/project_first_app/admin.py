from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, DriverLicense, Ownership, User

admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)


@admin.register(User)
class OwnerUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'passport_number', 'nationality')
    fieldsets = UserAdmin.fieldsets + (
        ('Данные владельца', {
            'fields': ('birth_date', 'passport_number', 'home_address', 'nationality'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные владельца', {
            'fields': ('first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality'),
        }),
    )
