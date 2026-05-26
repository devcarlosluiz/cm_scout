from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class League(TimeStampedModel):
    api_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    logo = models.URLField(blank=True)
    season = models.IntegerField(default=2024)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('League')
        verbose_name_plural = _('Leagues')
        ordering = ['country', 'name']
        indexes = [
            models.Index(fields=['is_active', 'season']),
        ]

    def __str__(self):
        return f'{self.name} ({self.country})'
