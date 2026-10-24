from django.contrib import admin

from .models import Conference, Review, TalkRegistration, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue_name', 'start_date', 'end_date')
    search_fields = ('title', 'venue_name', 'description')
    filter_horizontal = ('topics',)


@admin.register(TalkRegistration)
class TalkRegistrationAdmin(admin.ModelAdmin):
    list_display = ('talk_title', 'user', 'conference', 'recommended_for_publication')
    list_filter = ('conference', 'recommended_for_publication')
    search_fields = ('talk_title', 'user__username', 'user__last_name', 'conference__title')
    actions = ('mark_recommended', 'mark_not_recommended')

    @admin.action(description='Рекомендовать к публикации')
    def mark_recommended(self, request, queryset):
        updated = queryset.update(recommended_for_publication=True)
        self.message_user(request, f'Рекомендовано: {updated}')

    @admin.action(description='Не рекомендовать к публикации')
    def mark_not_recommended(self, request, queryset):
        updated = queryset.update(recommended_for_publication=False)
        self.message_user(request, f'Не рекомендовано: {updated}')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'conference', 'rating', 'conference_start', 'conference_end')
    list_filter = ('rating', 'conference')
    search_fields = ('text', 'author__username', 'author__last_name')
