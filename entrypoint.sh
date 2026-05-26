#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Creating cache table (fallback)..."
python manage.py createcachetable 2>/dev/null || true

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "==> Creating superuser (if not exists)..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'
username = email.split('@')[0]
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created.')
else:
    print('Superuser already exists.')
"
fi

if [ "$RUN_SYNC_ON_START" = "true" ]; then
    echo "==> Running sync_all..."
    python manage.py sync_all
fi

echo "==> Starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
