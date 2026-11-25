from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Car, DriverCar, DriverLicense, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Данные владельца автомобиля', {
            'fields': ('birth_date', 'passport_number', 'home_address', 'nationality'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные владельца автомобиля', {
            'fields': ('first_name', 'last_name', 'birth_date', 'passport_number',
                       'home_address', 'nationality'),
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'passport_number',
                    'home_address', 'nationality')


admin.site.register([Car, DriverLicense, DriverCar])