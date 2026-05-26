from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import FavoriteFixture
from apps.fixtures.models import Fixture


@login_required
def favorites_list(request):
    favorites = FavoriteFixture.objects.filter(
        user=request.user
    ).select_related(
        'fixture', 'fixture__home_team', 'fixture__away_team', 'fixture__league'
    ).order_by('fixture__fixture_date')
    return render(request, 'favorites/list.html', {'favorites': favorites})


@login_required
@require_POST
def toggle_favorite(request, fixture_pk):
    fixture = get_object_or_404(Fixture, pk=fixture_pk)
    fav, created = FavoriteFixture.objects.get_or_create(user=request.user, fixture=fixture)
    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    if request.headers.get('HX-Request'):
        return render(request, 'favorites/partials/toggle_btn.html', {
            'fixture': fixture, 'is_favorite': is_favorite
        })

    return JsonResponse({'is_favorite': is_favorite})
