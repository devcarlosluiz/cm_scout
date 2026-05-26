from django.contrib import admin
from .models import Bookmaker, Odd


@admin.register(Bookmaker)
class BookmakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('active',)


@admin.register(Odd)
class OddAdmin(admin.ModelAdmin):
    list_display = ('fixture', 'bookmaker', 'market', 'selection', 'odd', 'captured_at')
    list_filter = ('market', 'bookmaker')
    search_fields = ('fixture__home_team__name', 'fixture__away_team__name')
    raw_id_fields = ('fixture',)
    ordering = ('-captured_at',)
