from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Team, Player, Match, Prediction, Comment

# un: admin
# pw: basketballadmin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('display_name',)}),
    )
    list_display = ('username', 'email', 'display_name', 'is_staff')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'team', 'position', 'number')
    list_filter = ('team', 'position')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'date', 'status', 'home_score', 'away_score')
    list_filter = ('status', 'date')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'predicted_home_score', 'predicted_away_score', 'created_at')
    list_filter = ('user',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
