from django.db import models
from django.utils.translation import gettext_lazy as _


class Prediction(models.Model):
    class Confidence(models.TextChoices):
        LOW = 'low', _('Baixa')
        MEDIUM = 'medium', _('Média')
        HIGH = 'high', _('Alta')

    fixture = models.ForeignKey(
        'fixtures.Fixture',
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    market = models.CharField(max_length=20)
    market_label = models.CharField(max_length=100, blank=True)
    probability = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    score = models.IntegerField(default=0)
    confidence = models.CharField(max_length=10, choices=Confidence.choices, default=Confidence.LOW)
    reason = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Prediction')
        verbose_name_plural = _('Predictions')
        ordering = ['-score']
        unique_together = ['fixture', 'market']
        indexes = [
            models.Index(fields=['confidence', 'created_at']),
        ]

    def __str__(self):
        return f'{self.fixture} - {self.market} ({self.confidence})'

    @property
    def probability_pct(self):
        return round(float(self.probability) * 100, 1)
