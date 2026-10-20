from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership


class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Доп. информация', {'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')}),
    )
    list_display = UserAdmin.list_display + ('passport_number', 'nationality', 'home_address')


admin.site.register(CarOwner, CarOwnerAdmin)
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
