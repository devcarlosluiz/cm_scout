#!/usr/bin/env python
"""Roda todas as sincronizações: ligas, fixtures, standings, odds e análises."""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.leagues.tasks import sync_active_leagues, sync_standings_task
from apps.fixtures.tasks import sync_upcoming_fixtures
from apps.odds.tasks import sync_fixture_odds
from apps.analysis.tasks import recalculate_predictions


def run(label, fn, *args, **kwargs):
    print(f'\n>>> {label}...')
    try:
        result = fn(*args, **kwargs)
        print(f'    OK: {result}')
    except Exception as e:
        print(f'    ERRO: {e}')


if __name__ == '__main__':
    from services.football_api import FootballAPIService
    service = FootballAPIService()

    # 1. Ligas
    run('Sincronizando ligas', sync_active_leagues)

    # 2. Histórico completo da temporada (inclui partidas finalizadas para H2H e Forma Recente)
    #    Atenção: rate limit de 6s por liga — pode demorar alguns minutos
    run('Sincronizando fixtures históricos da temporada', service.sync_all_fixtures_for_season)

    # 3. Próximos 7 dias (garante fixtures futuros atualizados)
    run('Sincronizando fixtures próximos 7 dias', sync_upcoming_fixtures)

    # 4. Standings + estatísticas dos times
    run('Sincronizando standings', sync_standings_task)

    # 5. Odds
    run('Sincronizando odds', sync_fixture_odds)

    # 6. Análises/previsões
    run('Recalculando análises', recalculate_predictions)

    print('\nConcluído.')
