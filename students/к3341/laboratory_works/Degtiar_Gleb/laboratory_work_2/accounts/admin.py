from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import RegistrationForm, AccountChangeForm
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = RegistrationForm
    form = AccountChangeForm
    fieldsets = UserAdmin.fieldsets + (('Данные владельца', {'fields': ('birth_date','passport_number','address','nationality')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Данные владельца', {'fields': ('first_name','last_name','birth_date','passport_number','address','nationality')}),)
