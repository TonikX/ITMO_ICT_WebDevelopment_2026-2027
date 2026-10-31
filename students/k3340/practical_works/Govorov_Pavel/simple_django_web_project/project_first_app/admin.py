from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, DrivingLicense, Owner, Ownership


@admin.register(Owner)
class OwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Данные владельца",
            {
                "fields": [
                    "birth_date",
                    "passport_number",
                    "home_address",
                    "nationality",
                ]
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Данные владельца",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "birth_date",
                    "passport_number",
                    "home_address",
                    "nationality",
                ]
            },
        ),
    )


admin.site.register([Car, Ownership, DrivingLicense])
