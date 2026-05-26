from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_active_leagues(self):
    """Fetch and sync active leagues from API-Football."""
    try:
        from services.football_api import FootballAPIService
        service = FootballAPIService()
        result = service.sync_leagues()
        logger.info(f'Synced {result} leagues.')
        return result
    except Exception as exc:
        logger.error(f'Error syncing leagues: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def sync_standings_task(self):
    """Sync standings and recompute team statistics for all active leagues."""
    try:
        from services.football_api import FootballAPIService
        service = FootballAPIService()
        total = service.sync_standings()
        logger.info(f'Synced {total} standings.')
        service.compute_team_statistics()
        logger.info('Team statistics recomputed.')
        return total
    except Exception as exc:
        logger.error(f'Error syncing standings: {exc}')
        raise self.retry(exc=exc, countdown=120)
