from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Car, Possession


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'date_of_birth',
                'passport_number',
                'home_address',
                'nationality',
            )
        }),
    )


admin.site.register(Car)
admin.site.register(Possession)