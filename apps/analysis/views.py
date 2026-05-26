from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Avg
from .models import Prediction
from apps.fixtures.models import Fixture
from django.utils import timezone
from datetime import timedelta
import django_filters


class PredictionFilter(django_filters.FilterSet):
    confidence = django_filters.ChoiceFilter(choices=Prediction.Confidence.choices)
    market = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Prediction
        fields = ['confidence', 'market']


@login_required
def analysis_index(request):
    """Show top analysis opportunities."""
    upcoming = Fixture.objects.filter(
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=7),
        status=Fixture.Status.SCHEDULED,
    )

    high_confidence = Prediction.objects.filter(
        confidence='high',
        fixture__in=upcoming,
    ).select_related('fixture', 'fixture__home_team', 'fixture__away_team', 'fixture__league').order_by('-score')[:20]

    medium_confidence = Prediction.objects.filter(
        confidence='medium',
        fixture__in=upcoming,
    ).select_related('fixture', 'fixture__home_team', 'fixture__away_team', 'fixture__league').order_by('-score')[:20]

    market_stats = Prediction.objects.filter(
        fixture__in=upcoming,
        confidence__in=['medium', 'high'],
    ).values('market', 'market_label').annotate(count=Count('id'), avg_score=Avg('score')).order_by('-count')

    return render(request, 'analysis/index.html', {
        'high_confidence': high_confidence,
        'medium_confidence': medium_confidence,
        'market_stats': market_stats,
    })
