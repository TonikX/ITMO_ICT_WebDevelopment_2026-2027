from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Team,
    Car,
    DriverProfile,
    Race,
    Registration,
    RaceResult,
    Comment,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone',)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone',)
        }),
    )


admin.site.register(Team)
admin.site.register(Car)
admin.site.register(DriverProfile)
admin.site.register(Race)
admin.site.register(Registration)
admin.site.register(RaceResult)
admin.site.register(Comment)