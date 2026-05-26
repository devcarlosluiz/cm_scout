from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sincroniza ligas, fixtures históricos, standings, odds e análises.'

    def handle(self, *args, **options):
        from services.football_api import FootballAPIService
        from apps.leagues.tasks import sync_active_leagues, sync_standings_task
        from apps.fixtures.tasks import sync_upcoming_fixtures
        from apps.odds.tasks import sync_fixture_odds
        from apps.analysis.tasks import recalculate_predictions

        service = FootballAPIService()

        steps = [
            ('Ligas',                          sync_active_leagues),
            ('Fixtures históricos da temporada', service.sync_all_fixtures_for_season),
            ('Fixtures próximos 7 dias',        sync_upcoming_fixtures),
            ('Standings',                       sync_standings_task),
            ('Odds',                            sync_fixture_odds),
            ('Análises/previsões',              recalculate_predictions),
        ]

        for label, fn in steps:
            self.stdout.write(f'>>> {label}...')
            try:
                result = fn()
                self.stdout.write(self.style.SUCCESS(f'    OK: {result}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ERRO: {e}'))

        self.stdout.write(self.style.SUCCESS('Concluído.'))
