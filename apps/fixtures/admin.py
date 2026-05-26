from django.contrib import admin
from .models import Fixture


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'league', 'fixture_date', 'status', 'home_score', 'away_score')
    list_filter = ('status', 'league', 'fixture_date')
    search_fields = ('home_team__name', 'away_team__name', 'league__name')
    raw_id_fields = ('home_team', 'away_team', 'league')
    ordering = ('-fixture_date',)
    date_hierarchy = 'fixture_date'
