from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительно",
            {
                "fields": (
                    "passport_number",
                    "home_address",
                    "nationality",
                    "birth_date",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительно",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "passport_number",
                    "home_address",
                    "nationality",
                    "birth_date",
                )
            },
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "passport_number",
        "nationality",
        "is_staff",
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
