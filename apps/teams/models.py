from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Team(TimeStampedModel):
    api_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    logo = models.URLField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    founded = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['name']

    def __str__(self):
        return self.name
