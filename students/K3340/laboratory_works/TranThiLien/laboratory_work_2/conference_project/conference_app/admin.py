from django.contrib import admin
from .models import Conference, Topic, Venue, ConferenceTopic, Registration, Review


# ============================================================
# Conference Admin
# ============================================================
@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display   = ('title', 'venue', 'start_date', 'end_date')
    list_filter    = ('start_date', 'venue')
    search_fields  = ('title', 'description')
    date_hierarchy = 'start_date'


# ============================================================
# Registration Admin — với actions duyệt hàng loạt (Bài 2.3)
# ============================================================
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display  = ('report_title', 'conference', 'author', 'status', 'recommended', 'created_at')
    list_filter   = ('status', 'recommended', 'conference')
    search_fields = ('report_title', 'author__username')
    actions       = ['mark_recommended', 'mark_not_recommended', 'mark_approved', 'mark_rejected']

    @admin.action(description='✅ Предлагаемое объявление')
    def mark_recommended(self, request, queryset):
        queryset.update(recommended=True, status='approved')

    @admin.action(description='❌ Не рекомендуется')
    def mark_not_recommended(self, request, queryset):
        queryset.update(recommended=False, status='rejected')

    @admin.action(description='Утвеждать')
    def mark_approved(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Отклонить')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')


# ============================================================
# Review Admin
# ============================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('conference', 'author', 'rating', 'created_at')
    list_filter   = ('rating', 'conference')
    search_fields = ('text', 'author__username')


# ============================================================
# Các model còn lại
# ============================================================
admin.site.register(Topic)
admin.site.register(Venue)
admin.site.register(ConferenceTopic)