from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from apps.fixtures.models import Fixture
from apps.analysis.models import Prediction
from apps.odds.models import Odd
from apps.leagues.models import League


@login_required
def dashboard_index(request):
    """Main dashboard view."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    tomorrow_end = today_start + timedelta(days=2)
    week_end = today_start + timedelta(days=7)

    # Stats cards
    games_today = Fixture.objects.filter(
        fixture_date__gte=today_start,
        fixture_date__lt=tomorrow_start,
    ).count()

    games_tomorrow = Fixture.objects.filter(
        fixture_date__gte=tomorrow_start,
        fixture_date__lt=tomorrow_end,
    ).count()

    games_7_days = Fixture.objects.filter(
        fixture_date__gte=now,
        fixture_date__lte=week_end,
        status=Fixture.Status.SCHEDULED,
    ).count()

    opportunities = Prediction.objects.filter(
        confidence='high',
        fixture__fixture_date__gte=now,
        fixture__fixture_date__lte=week_end,
        fixture__status=Fixture.Status.SCHEDULED,
    ).count()

    odds_monitored = Odd.objects.filter(
        fixture__fixture_date__gte=now,
        fixture__fixture_date__lte=week_end,
    ).count()

    # Main table: upcoming fixtures with their best prediction
    upcoming_fixtures = Fixture.objects.filter(
        fixture_date__gte=now,
        fixture_date__lte=week_end,
        status=Fixture.Status.SCHEDULED,
    ).select_related(
        'league', 'home_team', 'away_team'
    ).prefetch_related(
        'predictions'
    ).order_by('fixture_date')[:30]

    # Chart data: fixtures per league
    fixtures_by_league = Fixture.objects.filter(
        fixture_date__gte=now,
        fixture_date__lte=week_end,
    ).values('league__name').annotate(count=Count('id')).order_by('-count')[:8]

    # Chart data: predictions by market
    predictions_by_market = Prediction.objects.filter(
        fixture__fixture_date__gte=now,
        fixture__fixture_date__lte=week_end,
        confidence__in=['medium', 'high'],
    ).values('market_label').annotate(count=Count('id')).order_by('-count')

    # Opportunities ranking
    top_opportunities = Prediction.objects.filter(
        confidence='high',
        fixture__fixture_date__gte=now,
        fixture__fixture_date__lte=week_end,
        fixture__status=Fixture.Status.SCHEDULED,
    ).select_related(
        'fixture', 'fixture__home_team', 'fixture__away_team', 'fixture__league'
    ).order_by('-score')[:10]

    return render(request, 'dashboard/index.html', {
        'games_today': games_today,
        'games_tomorrow': games_tomorrow,
        'games_7_days': games_7_days,
        'opportunities': opportunities,
        'odds_monitored': odds_monitored,
        'upcoming_fixtures': upcoming_fixtures,
        'fixtures_by_league': list(fixtures_by_league),
        'predictions_by_market': list(predictions_by_market),
        'top_opportunities': top_opportunities,
    })
