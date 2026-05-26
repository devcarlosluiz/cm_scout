from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_upcoming_fixtures(self):
    """Fetch fixtures for the next 7 days from API-Football."""
    try:
        from services.football_api import FootballAPIService
        service = FootballAPIService()
        result = service.sync_upcoming_fixtures()
        logger.info(f'Synced {result} fixtures.')
        return result
    except Exception as exc:
        logger.error(f'Error syncing fixtures: {exc}')
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3)
def sync_fixture_result(self, fixture_api_id: int):
    """Update result for a specific fixture."""
    try:
        from services.football_api import FootballAPIService
        service = FootballAPIService()
        return service.update_fixture_result(fixture_api_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
