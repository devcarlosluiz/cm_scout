from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch

from .models import Fixture
from .filters import FixtureFilter
from apps.odds.models import Odd
from apps.analysis.models import Prediction


@login_required
def fixture_list(request):
    """List upcoming fixtures with filters."""
    base_qs = Fixture.objects.filter(
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=7),
    ).select_related('league', 'home_team', 'away_team').order_by('fixture_date')

    fixture_filter = FixtureFilter(request.GET, queryset=base_qs)

    return render(request, 'fixtures/list.html', {
        'filter': fixture_filter,
        'fixtures': fixture_filter.qs,
        'total': fixture_filter.qs.count(),
    })


@login_required
def fixture_detail(request, pk):
    """Detailed view of a single fixture."""
    fixture = get_object_or_404(
        Fixture.objects.select_related('league', 'home_team', 'away_team'),
        pk=pk
    )

    odds = Odd.objects.filter(fixture=fixture).select_related('bookmaker').order_by('market', 'selection')
    predictions = Prediction.objects.filter(fixture=fixture).order_by('-confidence')

    # Head-to-head last 5
    from django.db.models import Q
    h2h = Fixture.objects.filter(
        Q(home_team=fixture.home_team, away_team=fixture.away_team) |
        Q(home_team=fixture.away_team, away_team=fixture.home_team),
        status=Fixture.Status.FINISHED,
    ).exclude(pk=fixture.pk).order_by('-fixture_date')[:5]

    # Recent form
    home_form = Fixture.objects.filter(
        Q(home_team=fixture.home_team) | Q(away_team=fixture.home_team),
        status=Fixture.Status.FINISHED,
    ).order_by('-fixture_date')[:5]

    away_form = Fixture.objects.filter(
        Q(home_team=fixture.away_team) | Q(away_team=fixture.away_team),
        status=Fixture.Status.FINISHED,
    ).order_by('-fixture_date')[:5]

    from apps.statistics.models import Standing, TeamStatistics
    home_standing = Standing.objects.filter(team=fixture.home_team, league=fixture.league).first()
    away_standing = Standing.objects.filter(team=fixture.away_team, league=fixture.league).first()
    home_stats = TeamStatistics.objects.filter(team=fixture.home_team, league=fixture.league).first()
    away_stats = TeamStatistics.objects.filter(team=fixture.away_team, league=fixture.league).first()

    is_favorite = False
    if request.user.is_authenticated:
        from apps.favorites.models import FavoriteFixture
        is_favorite = FavoriteFixture.objects.filter(user=request.user, fixture=fixture).exists()

    # Group odds by market
    odds_by_market = {}
    for odd in odds:
        if odd.market not in odds_by_market:
            odds_by_market[odd.market] = []
        odds_by_market[odd.market].append(odd)

    return render(request, 'fixtures/detail.html', {
        'fixture': fixture,
        'odds_by_market': odds_by_market,
        'predictions': predictions,
        'h2h': h2h,
        'home_form': home_form,
        'away_form': away_form,
        'home_standing': home_standing,
        'away_standing': away_standing,
        'home_stats': home_stats,
        'away_stats': away_stats,
        'is_favorite': is_favorite,
    })


@login_required
def fixture_list_htmx(request):
    """HTMX partial: filtered fixture rows."""
    base_qs = Fixture.objects.filter(
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=7),
    ).select_related('league', 'home_team', 'away_team').order_by('fixture_date')

    fixture_filter = FixtureFilter(request.GET, queryset=base_qs)
    return render(request, 'fixtures/partials/fixture_rows.html', {
        'fixtures': fixture_filter.qs,
    })
