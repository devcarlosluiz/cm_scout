from django.contrib import admin
from .models import League


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'season', 'is_active', 'created_at')
    list_filter = ('is_active', 'country', 'season')
    search_fields = ('name', 'country')
    list_editable = ('is_active',)
    ordering = ('country', 'name')
