from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CarOwner, Car, Ownership, DriverLicense


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'email', 'nationality', 'passport')
    search_fields = ('username', 'last_name', 'first_name', 'passport')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'passport', 'address', 'nationality'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'passport', 'address', 'nationality'),
        }),
    )

admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)