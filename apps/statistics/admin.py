from django.contrib import admin
from .models import Standing, TeamStatistics


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('team', 'league', 'season', 'position', 'points', 'wins', 'draws', 'losses')
    list_filter = ('league', 'season')
    search_fields = ('team__name', 'league__name')
    ordering = ('league', 'position')


@admin.register(TeamStatistics)
class TeamStatisticsAdmin(admin.ModelAdmin):
    list_display = ('team', 'league', 'season', 'avg_goals_scored', 'over25_rate', 'both_teams_score_rate')
    list_filter = ('league', 'season')
    search_fields = ('team__name',)
