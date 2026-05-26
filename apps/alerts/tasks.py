from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_user_alerts():
    """Check all active alerts against new predictions and notify users."""
    from apps.alerts.models import Alert
    from apps.analysis.models import Prediction
    from apps.fixtures.models import Fixture
    from django.utils import timezone
    from datetime import timedelta

    upcoming = Fixture.objects.filter(
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=24),
        status=Fixture.Status.SCHEDULED,
    )

    recent_predictions = Prediction.objects.filter(
        fixture__in=upcoming,
        confidence__in=['medium', 'high'],
    ).select_related('fixture', 'fixture__home_team', 'fixture__away_team', 'fixture__league')

    active_alerts = Alert.objects.filter(active=True).select_related('user', 'league')

    notifications_sent = 0
    for alert in active_alerts:
        for prediction in recent_predictions:
            if alert.matches_prediction(prediction):
                _send_alert_notification(alert, prediction)
                notifications_sent += 1

    logger.info(f'Sent {notifications_sent} alert notifications.')
    return notifications_sent


def _send_alert_notification(alert, prediction):
    """Send email or in-app notification for a matched alert."""
    from django.utils import timezone

    try:
        if alert.send_email and alert.user.notification_email:
            from django.core.mail import send_mail
            from django.conf import settings

            subject = f'[ScoutBet] Alerta: {prediction.market_label} - {prediction.fixture}'
            message = (
                f'Seu alerta "{alert.name}" foi acionado!\n\n'
                f'Partida: {prediction.fixture}\n'
                f'Mercado: {prediction.market_label}\n'
                f'Confiança: {prediction.get_confidence_display()}\n'
                f'Score: {prediction.score}/100\n'
                f'Motivo: {prediction.reason}\n\n'
                f'Acesse: https://scoutbet.com/fixtures/{prediction.fixture.pk}/'
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [alert.user.email],
                fail_silently=True,
            )

        alert.last_triggered = timezone.now()
        alert.save(update_fields=['last_triggered'])
    except Exception as e:
        logger.error(f'Error sending alert notification: {e}')
