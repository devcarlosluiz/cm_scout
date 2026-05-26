from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Team


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    from apps.statistics.models import TeamStatistics, Standing
    from apps.fixtures.models import Fixture
    from django.utils import timezone

    stats = TeamStatistics.objects.filter(team=team).select_related('league').first()
    standings = Standing.objects.filter(team=team).select_related('league').order_by('-league__season')

    recent_fixtures = Fixture.objects.filter(
        models.Q(home_team=team) | models.Q(away_team=team),
        status='FT',
    ).select_related('league', 'home_team', 'away_team').order_by('-fixture_date')[:5]

    return render(request, 'teams/detail.html', {
        'team': team,
        'stats': stats,
        'standings': standings,
        'recent_fixtures': recent_fixtures,
    })


from django.db import models
