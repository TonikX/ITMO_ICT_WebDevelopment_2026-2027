from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CarOwner, Car, Ownership, DriverLicense

class CustomUserAdmin(UserAdmin):
    # добавляем наши новые поля к стандартным полям пользователя в админке
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')
        }),
    )
    # добавляем поля на экран создания пользователя в админке
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality')
        }),
    )

admin.site.register(CarOwner, CustomUserAdmin)
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)