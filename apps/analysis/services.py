"""
Analysis service: orchestrates all engines for a given fixture.
"""
import logging
from apps.analysis.engines import get_all_engines
from apps.analysis.models import Prediction
from apps.statistics.models import TeamStatistics
from apps.fixtures.models import Fixture

logger = logging.getLogger(__name__)


def run_analysis_for_fixture(fixture: Fixture) -> list:
    """
    Run all analysis engines for a fixture and persist predictions.
    Returns list of created/updated Prediction objects.
    """
    home_stats = TeamStatistics.objects.filter(
        team=fixture.home_team, league=fixture.league
    ).first()
    away_stats = TeamStatistics.objects.filter(
        team=fixture.away_team, league=fixture.league
    ).first()

    from django.db.models import Q
    h2h = Fixture.objects.filter(
        Q(home_team=fixture.home_team, away_team=fixture.away_team) |
        Q(home_team=fixture.away_team, away_team=fixture.home_team),
        status=Fixture.Status.FINISHED,
    ).exclude(pk=fixture.pk).order_by('-fixture_date')[:5]

    results = []
    for engine in get_all_engines():
        try:
            result = engine.calculate(fixture, home_stats, away_stats, h2h)
            if result is None:
                continue

            prediction, _ = Prediction.objects.update_or_create(
                fixture=fixture,
                market=result.market,
                defaults={
                    'market_label': engine.market_name,
                    'probability': result.probability,
                    'score': result.score,
                    'confidence': result.confidence,
                    'reason': result.reason,
                    'details': result.details,
                }
            )
            results.append(prediction)
        except Exception as e:
            logger.error(f'Engine {engine.__class__.__name__} error for fixture {fixture.pk}: {e}')

    return results


def run_analysis_bulk(fixture_ids: list) -> int:
    """Run analysis for multiple fixtures."""
    fixtures = Fixture.objects.filter(
        pk__in=fixture_ids
    ).select_related('home_team', 'away_team', 'league')

    count = 0
    for fixture in fixtures:
        try:
            run_analysis_for_fixture(fixture)
            count += 1
        except Exception as e:
            logger.error(f'Bulk analysis error for fixture {fixture.pk}: {e}')

    return count
