from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CarOwner, DriverLicense, Car, Ownership, User

admin.site.register(CarOwner)
admin.site.register(DriverLicense)
admin.site.register(Car)
admin.site.register(Ownership)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('name', 'passport_number', 'home_address', 'nationality')}),
    )
    list_display = ('username', 'email', 'name', 'first_name', 'last_name', 'is_staff', 'nationality')

admin.site.register(User, CustomUserAdmin)