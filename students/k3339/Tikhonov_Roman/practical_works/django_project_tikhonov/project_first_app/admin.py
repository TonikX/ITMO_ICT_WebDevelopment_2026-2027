from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Car, DriverLicense, Ownership, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Дополнительные сведения", {
            "fields": ("birth_date", "passport_number", "home_address", "nationality"),
        }),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Дополнительные сведения", {
            "fields": ("birth_date", "passport_number", "home_address", "nationality"),
        }),
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
