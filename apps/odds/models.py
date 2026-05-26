from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Bookmaker(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    api_id = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Bookmaker')
        verbose_name_plural = _('Bookmakers')
        ordering = ['name']

    def __str__(self):
        return self.name


class Odd(models.Model):
    class Market(models.TextChoices):
        MATCH_WINNER = '1X2', _('1X2 - Resultado')
        BOTH_TEAMS_SCORE = 'BTTS', _('Ambas Marcam')
        OVER_15 = 'OVER_15', _('Over 1.5 Gols')
        OVER_25 = 'OVER_25', _('Over 2.5 Gols')
        OVER_35 = 'OVER_35', _('Over 3.5 Gols')
        ASIAN_HANDICAP = 'AH', _('Asian Handicap')
        DOUBLE_CHANCE = 'DC', _('Dupla Chance')
        DRAW_NO_BET = 'DNB', _('Draw No Bet')

    fixture = models.ForeignKey(
        'fixtures.Fixture',
        on_delete=models.CASCADE,
        related_name='odds'
    )
    bookmaker = models.ForeignKey(
        Bookmaker,
        on_delete=models.CASCADE,
        related_name='odds'
    )
    market = models.CharField(max_length=20, choices=Market.choices)
    selection = models.CharField(max_length=100)
    odd = models.DecimalField(max_digits=6, decimal_places=2)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Odd')
        verbose_name_plural = _('Odds')
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['fixture', 'market']),
            models.Index(fields=['captured_at']),
        ]

    def __str__(self):
        return f'{self.fixture} - {self.get_market_display()} - {self.selection}: {self.odd}'
