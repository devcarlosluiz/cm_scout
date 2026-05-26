from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_data():
    """Remove odds and logs older than 30 days."""
    from django.utils import timezone
    from datetime import timedelta
    from apps.core.models import AuditLog
    from apps.odds.models import Odd

    cutoff = timezone.now() - timedelta(days=30)

    deleted_logs, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    deleted_odds, _ = Odd.objects.filter(captured_at__lt=cutoff).delete()

    logger.info(f'Cleanup: {deleted_logs} audit logs, {deleted_odds} odds removed.')
    return {'audit_logs': deleted_logs, 'odds': deleted_odds}
