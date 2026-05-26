from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_fixture_odds(self):
    """Sync odds for upcoming fixtures."""
    try:
        from services.odds_api import OddsAPIService
        service = OddsAPIService()
        result = service.sync_upcoming_odds()
        logger.info(f'Synced odds for {result} fixtures.')
        return result
    except Exception as exc:
        logger.error(f'Error syncing odds: {exc}')
        raise self.retry(exc=exc, countdown=60)
