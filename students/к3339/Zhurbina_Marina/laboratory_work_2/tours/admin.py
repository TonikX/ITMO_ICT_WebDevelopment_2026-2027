from django.contrib import admin

from .models import Agency, Reservation, Review, Tour


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'agency', 'date_start', 'date_end', 'price')
    list_filter = ('country', 'agency')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'guests', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['make_confirmed']

    def make_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'Подтверждено броней: {updated}')
    make_confirmed.short_description = 'Подтвердить выбранные брони'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'tour', 'rating', 'created_at')
