from django.contrib import admin
from .models import Country, TourAgency, Tour, Reservation, Review


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


@admin.register(TourAgency)
class TourAgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email')
    search_fields = ('name', )


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'agency', 'country',
        'start_date', 'end_date', 'price',
        'payment_terms', 'sold_count'
    )
    list_filter = ('country', 'agency', 'payment_terms', 'start_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tour', 'participants_count', 'status', 'created_at')
    list_filter = ('status', 'tour__country', 'created_at')
    search_fields = ('user__username', 'tour__name')
    actions = ['confirm_reservations']

    @admin.action(description='Подтвердить выбранные резервирования')
    def confirm_reservations(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'Подтверждено резервирований: {updated}')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tour', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'tour__name', 'text')