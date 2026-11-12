from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CarOwner, Car, Ownership, DriverLicense


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные данные', {
            'fields': (
                'birth_date',
                'passport_number',
                'home_address',
                'nationality'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные владельца', {
            'fields': (
                'first_name',
                'last_name',
                'birth_date',
                'passport_number',
                'home_address',
                'nationality'
            )
        }),
    )

admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
