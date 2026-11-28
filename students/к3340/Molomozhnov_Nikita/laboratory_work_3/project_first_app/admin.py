from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CarOwner, Car, Ownership, DriverLicense


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(CarOwner)
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
