from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import League


@login_required
def league_list(request):
    leagues = League.objects.filter(is_active=True).order_by('country', 'name')
    return render(request, 'leagues/list.html', {'leagues': leagues})


@login_required
def league_detail(request, pk):
    league = get_object_or_404(League, pk=pk)
    from apps.fixtures.models import Fixture
    from apps.statistics.models import Standing
    from django.utils import timezone
    from datetime import timedelta

    upcoming = Fixture.objects.filter(
        league=league,
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=7),
    ).select_related('home_team', 'away_team').order_by('fixture_date')

    recent = Fixture.objects.filter(
        league=league,
        status='FT',
    ).select_related('home_team', 'away_team').order_by('-fixture_date')[:10]

    standings = Standing.objects.filter(
        league=league,
        season=league.season,
    ).select_related('team').order_by('position')

    return render(request, 'leagues/detail.html', {
        'league': league,
        'upcoming_fixtures': upcoming,
        'recent_fixtures': recent,
        'standings': standings,
    })
