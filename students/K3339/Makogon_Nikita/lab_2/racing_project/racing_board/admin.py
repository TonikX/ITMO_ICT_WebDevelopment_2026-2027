from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import RacerUser, Race, RaceRegistration, Comment

class RacerUserAdmin(UserAdmin):
    # добавляем новые поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Информация о гонщике', {
            'fields': ('full_name', 'team_name', 'racer_class', 'experience', 'racer_description', 'car_description')
        }),
    )
    # добавляем новые поля в форму создания пользователя в админке
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Информация о гонщике', {
            'fields': ('full_name', 'team_name', 'racer_class', 'experience')
        }),
    )
    list_display = ('username', 'full_name', 'team_name', 'racer_class', 'experience')
    list_filter = ('racer_class', 'team_name')

class RaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'track', 'race_date', 'is_completed')
    list_filter = ('is_completed', 'race_date')

class RaceRegistrationAdmin(admin.ModelAdmin):
    list_display = ('racer', 'race', 'car_number', 'result_place', 'race_time', 'result_status')
    list_filter = ('race', 'result_status')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'race', 'rating', 'comment_type', 'created_at')
    list_filter = ('comment_type', 'rating')

# регистрируем модели
admin.site.register(RacerUser, RacerUserAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(RaceRegistration, RaceRegistrationAdmin)
admin.site.register(Comment, CommentAdmin)