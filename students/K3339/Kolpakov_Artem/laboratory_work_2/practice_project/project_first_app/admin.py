from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, DriverLicense, Ownership, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительные данные",
            {
                "fields": (
                    "birth_date",
                    "passport_number",
                    "home_address",
                    "nationality",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительные данные",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_date",
                    "passport_number",
                    "home_address",
                    "nationality",
                )
            },
        ),
    )


admin.site.register(DriverLicense)
admin.site.register(Car)
admin.site.register(Ownership)
