import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('scoutbet')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Scheduled Tasks (Celery Beat)
app.conf.beat_schedule = {
    # Every 6 hours: update leagues
    'update-leagues': {
        'task': 'apps.leagues.tasks.sync_active_leagues',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Every 1 hour: update fixtures
    'update-fixtures': {
        'task': 'apps.fixtures.tasks.sync_upcoming_fixtures',
        'schedule': crontab(minute=0),
    },
    # Every 30 minutes: update odds
    'update-odds': {
        'task': 'apps.odds.tasks.sync_fixture_odds',
        'schedule': crontab(minute='*/30'),
    },
    # Every 15 minutes: recalculate analyses
    'recalculate-analysis': {
        'task': 'apps.analysis.tasks.recalculate_predictions',
        'schedule': crontab(minute='*/15'),
    },
    # Every hour: check and send alerts
    'check-alerts': {
        'task': 'apps.alerts.tasks.process_user_alerts',
        'schedule': crontab(minute=5),
    },
    # Every day at midnight: cleanup old data
    'cleanup-old-data': {
        'task': 'apps.core.tasks.cleanup_old_data',
        'schedule': crontab(minute=0, hour=0),
    },
    # Every day at 3am: sync standings and recompute team stats
    'sync-standings-daily': {
        'task': 'apps.leagues.tasks.sync_standings_task',
        'schedule': crontab(minute=0, hour=3),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
