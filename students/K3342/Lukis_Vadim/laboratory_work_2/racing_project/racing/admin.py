from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CarOwner, Car, Ownership
from .models import Racer, Race, RaceRegistration, Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('passport_number', 'home_address', 'nationality')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'passport_number', 'nationality', 'is_staff')


@admin.register(CarOwner)
class CarOwnerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'passport_number')
    search_fields = ('last_name', 'first_name', 'passport_number')
    list_filter = ('birth_date',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model', 'color', 'year')
    search_fields = ('license_plate', 'brand', 'model')
    list_filter = ('brand', 'color', 'year')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('car_owner', 'car', 'start_date', 'end_date')
    search_fields = ('car_owner__last_name', 'car__license_plate')
    list_filter = ('start_date', 'end_date')


@admin.register(Racer)
class RacerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'team_name', 'experience', 'racer_class')
    search_fields = ('last_name', 'first_name', 'team_name')
    list_filter = ('racer_class', 'experience')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'race_date', 'track_location')
    search_fields = ('name', 'track_location')
    list_filter = ('race_date',)
    date_hierarchy = 'race_date'


@admin.register(RaceRegistration)
class RaceRegistrationAdmin(admin.ModelAdmin):
    list_display = ('racer', 'race', 'race_time', 'result', 'registration_date')
    list_editable = ('race_time', 'result')
    search_fields = ('racer__last_name', 'race__name')
    list_filter = ('race',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('race', 'author', 'comment_type', 'rating', 'created_at')
    search_fields = ('race__name', 'author__username', 'comment_text')
    list_filter = ('comment_type', 'rating', 'created_at')
    date_hierarchy = 'created_at'
