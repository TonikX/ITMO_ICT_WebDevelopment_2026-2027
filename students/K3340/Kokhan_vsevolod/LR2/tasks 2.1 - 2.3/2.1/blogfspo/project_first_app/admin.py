from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Car, Ownership, DrivingLicense


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Личная информация', {
            'fields': (
                'passport_number',
                'address',
                'nationality'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Личная информация', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'passport_number',
                'address',
                'nationality'
            )
        }),
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DrivingLicense)