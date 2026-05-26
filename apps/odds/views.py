from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Odd
from apps.fixtures.models import Fixture


@login_required
def odds_history(request, fixture_pk):
    """Show odds history chart for a fixture."""
    fixture = get_object_or_404(Fixture, pk=fixture_pk)
    market = request.GET.get('market', Odd.Market.MATCH_WINNER)

    odds = Odd.objects.filter(
        fixture=fixture, market=market
    ).select_related('bookmaker').order_by('captured_at')

    if request.headers.get('HX-Request'):
        return render(request, 'odds/partials/history_chart.html', {
            'fixture': fixture, 'odds': odds, 'market': market,
        })

    return render(request, 'odds/history.html', {
        'fixture': fixture, 'odds': odds, 'market': market,
        'markets': Odd.Market.choices,
    })
