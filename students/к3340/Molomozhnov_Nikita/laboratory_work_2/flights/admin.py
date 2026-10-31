from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Airline, Flight, Reservation, Review


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('passport_number', 'home_address', 'nationality')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Airline)
admin.site.register(Flight)
admin.site.register(Reservation)
admin.site.register(Review)
