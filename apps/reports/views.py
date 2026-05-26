from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg

from apps.analysis.models import Prediction
from apps.fixtures.models import Fixture


@login_required
def reports_index(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    predictions_by_confidence = Prediction.objects.filter(
        fixture__fixture_date__gte=month_ago,
    ).values('confidence').annotate(count=Count('id'))

    top_leagues = Prediction.objects.filter(
        confidence='high',
        fixture__fixture_date__gte=month_ago,
    ).values('fixture__league__name').annotate(
        count=Count('id'),
        avg_score=Avg('score'),
    ).order_by('-count')[:10]

    return render(request, 'reports/index.html', {
        'predictions_by_confidence': predictions_by_confidence,
        'top_leagues': top_leagues,
    })
