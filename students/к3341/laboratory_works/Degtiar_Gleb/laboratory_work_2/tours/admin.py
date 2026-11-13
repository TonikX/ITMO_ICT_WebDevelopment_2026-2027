from django.contrib import admin
from .models import Country, Agency, Tour, Booking, Review
from .services import confirm_booking
admin.site.register(Country)
admin.site.register(Agency)
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display=('title','country','agency','start_date','end_date','price','is_active')
    list_filter=('country','agency','is_active')
    search_fields=('title','description')
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display=('user','tour','travelers','status','unit_price','created_at')
    list_filter=('status','tour__country')
    search_fields=('user__username','tour__title')
    readonly_fields=('created_at',)
    actions=['confirm_selected']
    @admin.action(description='Подтвердить выбранные бронирования')
    def confirm_selected(self,request,queryset):
        for pk in queryset.values_list('pk',flat=True): confirm_booking(pk)
        self.message_user(request,'Бронирования подтверждены.')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=('tour','user','rating','start_date','end_date')
    list_filter=('rating',)
