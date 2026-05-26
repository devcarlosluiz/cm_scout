from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('fixture', 'market_label', 'score', 'confidence', 'probability_pct', 'updated_at')
    list_filter = ('confidence', 'market')
    search_fields = ('fixture__home_team__name', 'fixture__away_team__name')
    raw_id_fields = ('fixture',)
    ordering = ('-score',)
    readonly_fields = ('created_at', 'updated_at')
