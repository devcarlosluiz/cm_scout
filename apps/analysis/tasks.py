from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def recalculate_predictions(self):
    """Recalculate predictions for all upcoming fixtures."""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from apps.fixtures.models import Fixture
        from apps.analysis.services import run_analysis_bulk

        upcoming_ids = list(Fixture.objects.filter(
            fixture_date__gte=timezone.now(),
            fixture_date__lte=timezone.now() + timedelta(days=7),
            status=Fixture.Status.SCHEDULED,
        ).values_list('pk', flat=True))

        count = run_analysis_bulk(upcoming_ids)
        logger.info(f'Recalculated predictions for {count} fixtures.')
        return count
    except Exception as exc:
        logger.error(f'Error recalculating predictions: {exc}')
        raise self.retry(exc=exc, countdown=120)


@shared_task
def analyze_single_fixture(fixture_pk: int):
    """Run analysis for a single fixture."""
    from apps.fixtures.models import Fixture
    from apps.analysis.services import run_analysis_for_fixture

    try:
        fixture = Fixture.objects.get(pk=fixture_pk)
        results = run_analysis_for_fixture(fixture)
        return len(results)
    except Fixture.DoesNotExist:
        logger.warning(f'Fixture {fixture_pk} not found.')
        return 0
