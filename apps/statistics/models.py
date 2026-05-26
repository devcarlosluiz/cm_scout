from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Standing(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='standings')
    league = models.ForeignKey('leagues.League', on_delete=models.CASCADE, related_name='standings')
    season = models.IntegerField(default=2024)
    position = models.IntegerField()
    points = models.IntegerField(default=0)
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Standing')
        verbose_name_plural = _('Standings')
        ordering = ['position']
        unique_together = ['team', 'league', 'season']
        indexes = [
            models.Index(fields=['league', 'season', 'position']),
        ]

    def __str__(self):
        return f'{self.team} - {self.league} - P{self.position}'

    @property
    def win_rate(self):
        if self.played == 0:
            return 0
        return round((self.wins / self.played) * 100, 1)


class TeamStatistics(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='statistics')
    league = models.ForeignKey('leagues.League', on_delete=models.CASCADE, related_name='team_stats')
    season = models.IntegerField(default=2024)

    # Form
    last_5_wins = models.IntegerField(default=0)
    last_5_draws = models.IntegerField(default=0)
    last_5_losses = models.IntegerField(default=0)

    # Scoring
    avg_goals_scored = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    avg_goals_conceded = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    # Market rates (0-100)
    both_teams_score_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    over25_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    over15_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    clean_sheet_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fail_to_score_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Home/Away splits
    home_avg_goals_scored = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    home_avg_goals_conceded = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    away_avg_goals_scored = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    away_avg_goals_conceded = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Team Statistics')
        verbose_name_plural = _('Team Statistics')
        unique_together = ['team', 'league', 'season']

    def __str__(self):
        return f'{self.team} stats - {self.league}'

    @property
    def form_string(self):
        """Returns e.g. 'WWDLW' from last 5."""
        results = []
        results.extend(['W'] * self.last_5_wins)
        results.extend(['D'] * self.last_5_draws)
        results.extend(['L'] * self.last_5_losses)
        return ''.join(results[:5])

    @property
    def avg_total_goals(self):
        return float(self.avg_goals_scored) + float(self.avg_goals_conceded)
