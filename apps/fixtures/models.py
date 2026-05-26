from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Fixture(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = 'NS', _('Not Started')
        LIVE = 'LIVE', _('Live')
        HALFTIME = 'HT', _('Half Time')
        FINISHED = 'FT', _('Finished')
        POSTPONED = 'PST', _('Postponed')
        CANCELLED = 'CANC', _('Cancelled')

    api_id = models.IntegerField(unique=True, db_index=True)
    league = models.ForeignKey(
        'leagues.League',
        on_delete=models.CASCADE,
        related_name='fixtures'
    )
    home_team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='home_fixtures'
    )
    away_team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='away_fixtures'
    )
    fixture_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    round = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Fixture')
        verbose_name_plural = _('Fixtures')
        ordering = ['fixture_date']
        indexes = [
            models.Index(fields=['fixture_date', 'status']),
            models.Index(fields=['league', 'fixture_date']),
        ]

    def __str__(self):
        return f'{self.home_team} vs {self.away_team} - {self.fixture_date:%d/%m/%Y %H:%M}'

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.fixture_date > timezone.now() and self.status == self.Status.SCHEDULED

    @property
    def total_goals(self):
        if self.home_score is not None and self.away_score is not None:
            return self.home_score + self.away_score
        return None

    @property
    def result(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return 'home'
        elif self.away_score > self.home_score:
            return 'away'
        return 'draw'
