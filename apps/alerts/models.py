from django.db import models
from django.utils.translation import gettext_lazy as _


class Alert(models.Model):
    class Market(models.TextChoices):
        MATCH_WINNER = '1X2', _('Resultado')
        BTTS = 'BTTS', _('Ambas Marcam')
        OVER_25 = 'OVER_25', _('Over 2.5 Gols')
        OVER_15 = 'OVER_15', _('Over 1.5 Gols')
        HANDICAP = 'AH', _('Asian Handicap')
        ANY = 'ANY', _('Qualquer Mercado')

    class Confidence(models.TextChoices):
        LOW = 'low', _('Baixa')
        MEDIUM = 'medium', _('Média')
        HIGH = 'high', _('Alta')
        ANY = 'any', _('Qualquer')

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    name = models.CharField(max_length=255)
    market = models.CharField(max_length=20, choices=Market.choices, default=Market.ANY)
    minimum_odd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_confidence = models.CharField(
        max_length=10,
        choices=Confidence.choices,
        default=Confidence.HIGH
    )
    league = models.ForeignKey(
        'leagues.League',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    active = models.BooleanField(default=True)
    send_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.name}'

    def matches_prediction(self, prediction) -> bool:
        """Check if a prediction matches this alert's criteria."""
        if self.market != self.Market.ANY and prediction.market != self.market:
            return False

        if self.minimum_confidence != self.Confidence.ANY:
            confidence_order = {'low': 1, 'medium': 2, 'high': 3}
            pred_level = confidence_order.get(prediction.confidence, 0)
            min_level = confidence_order.get(self.minimum_confidence, 0)
            if pred_level < min_level:
                return False

        if self.league and prediction.fixture.league_id != self.league_id:
            return False

        return True
