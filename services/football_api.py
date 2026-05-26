"""
Football API Service (football-data.org v4)
Provides a decoupled integration layer with Redis caching.
"""
import logging
import hashlib
import json
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# football-data.org status → internal status mapping
STATUS_MAP = {
    'SCHEDULED': 'NS',
    'TIMED': 'NS',
    'IN_PLAY': '1H',
    'PAUSED': 'HT',
    'FINISHED': 'FT',
    'SUSPENDED': 'SUSP',
    'POSTPONED': 'PST',
    'CANCELLED': 'CANC',
    'AWARDED': 'AWD',
}


class FootballAPIService:
    """
    Wraps the football-data.org v4 REST API.
    All responses are cached in Redis to reduce API calls.
    Rate limit: 10 req/min on free plan.
    """

    BASE_URL = settings.FOOTBALL_DATA_BASE_URL
    SUPPORTED_LEAGUE_IDS = list(settings.SUPPORTED_LEAGUES.values())
    SUPPORTED_COMPETITIONS = settings.SUPPORTED_COMPETITIONS

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'X-Auth-Token': settings.FOOTBALL_DATA_API_KEY,
        })

    def _get(self, endpoint: str, params: dict = None, cache_ttl: int = None) -> Optional[dict]:
        """Make a GET request with Redis caching."""
        params = params or {}
        cache_key = self._build_cache_key(endpoint, params)

        if cache_ttl is None:
            cache_ttl = settings.API_CACHE_TTL_MEDIUM

        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f'Cache HIT: {cache_key}')
            return cached

        url = f'{self.BASE_URL}/{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            cache.set(cache_key, data, cache_ttl)
            logger.debug(f'API call: {url} → success')
            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f'API HTTP error for {endpoint}: {e} — {response.text[:300]}')
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f'API request failed for {endpoint}: {e}')
            return None

    def _build_cache_key(self, endpoint: str, params: dict) -> str:
        key_data = f'{endpoint}:{json.dumps(params, sort_keys=True)}'
        return f'football_api:{hashlib.md5(key_data.encode()).hexdigest()}'

    # -----------------------------------------------------------------------
    # Leagues
    # -----------------------------------------------------------------------

    def sync_leagues(self) -> int:
        """Fetch and upsert all supported competitions from football-data.org."""
        from apps.leagues.models import League

        data = self._get('competitions', cache_ttl=settings.API_CACHE_TTL_LONG)
        if not data:
            return 0

        supported_ids = set(self.SUPPORTED_LEAGUE_IDS)
        count = 0

        for comp in data.get('competitions', []):
            comp_id = comp.get('id')
            if comp_id not in supported_ids:
                continue

            area = comp.get('area', {})
            current_season = comp.get('currentSeason') or {}
            season_year = 2025
            if current_season.get('startDate'):
                season_year = int(current_season['startDate'][:4])

            League.objects.update_or_create(
                api_id=comp_id,
                defaults={
                    'name': comp.get('name', ''),
                    'country': area.get('name', ''),
                    'logo': comp.get('emblem', ''),
                    'season': season_year,
                    'is_active': True,
                }
            )
            count += 1
            logger.info(f'Synced league: {comp.get("name")} (id={comp_id})')

        return count

    # -----------------------------------------------------------------------
    # Fixtures
    # -----------------------------------------------------------------------

    def sync_upcoming_fixtures(self) -> int:
        """Fetch fixtures for the next 7 days — single request for all competitions."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        date_from = now.strftime('%Y-%m-%d')
        date_to = (now + timedelta(days=7)).strftime('%Y-%m-%d')

        comp_codes = ','.join(self.SUPPORTED_COMPETITIONS.values())

        data = self._get('matches', params={
            'competitions': comp_codes,
            'dateFrom': date_from,
            'dateTo': date_to,
        }, cache_ttl=settings.API_CACHE_TTL_SHORT)

        if not data:
            return 0

        matches = data.get('matches', [])
        logger.info(f'Fetched {len(matches)} upcoming matches')
        return self._process_fixtures(matches)

    def sync_all_fixtures_for_season(self, season: int = None) -> int:
        """
        Fetch all fixtures for each competition using its own current season year.
        BSA uses 2026, European leagues use 2025, etc. — pulled from the League model.
        One request per competition to avoid the 10-day date-range limit.
        """
        import time
        from apps.leagues.models import League as _League

        # Build code → season_year map from DB (falls back to provided season or 2025)
        fallback = season or 2025
        season_map = {}
        for key, comp_id in settings.SUPPORTED_LEAGUES.items():
            code = settings.SUPPORTED_COMPETITIONS.get(key)
            if not code:
                continue
            league_obj = _League.objects.filter(api_id=comp_id).first()
            season_map[code] = league_obj.season if league_obj else fallback

        total = 0
        for key, code in self.SUPPORTED_COMPETITIONS.items():
            comp_season = season_map.get(code, fallback)
            data = self._get(
                f'competitions/{code}/matches',
                params={'season': comp_season},
                cache_ttl=settings.API_CACHE_TTL_MEDIUM,
            )
            time.sleep(6)  # 10 req/min rate limit

            if not data:
                logger.warning(f'No data for competition {code} season {comp_season}')
                continue

            matches = data.get('matches', [])
            logger.info(f'{code} (season={comp_season}): {len(matches)} matches found')
            total += self._process_fixtures(matches)

        return total

    def _process_fixtures(self, matches_data: list) -> int:
        from apps.fixtures.models import Fixture
        from apps.leagues.models import League
        from apps.teams.models import Team
        from django.utils.dateparse import parse_datetime

        supported_ids = set(self.SUPPORTED_LEAGUE_IDS)
        count = 0

        for match in matches_data:
            comp = match.get('competition', {})
            home_data = match.get('homeTeam', {})
            away_data = match.get('awayTeam', {})
            score = match.get('score', {})
            area = match.get('area', {})

            comp_id = comp.get('id')
            if comp_id not in supported_ids:
                continue

            home_id = home_data.get('id')
            away_id = away_data.get('id')
            match_id = match.get('id')
            if not home_id or not away_id or not match_id:
                continue

            # Upsert league
            league, _ = League.objects.get_or_create(
                api_id=comp_id,
                defaults={
                    'name': comp.get('name', ''),
                    'country': area.get('name', ''),
                    'logo': comp.get('emblem', ''),
                }
            )

            # Upsert teams
            home_team, _ = Team.objects.get_or_create(
                api_id=home_id,
                defaults={
                    'name': home_data.get('name', ''),
                    'logo': home_data.get('crest', ''),
                }
            )
            away_team, _ = Team.objects.get_or_create(
                api_id=away_id,
                defaults={
                    'name': away_data.get('name', ''),
                    'logo': away_data.get('crest', ''),
                }
            )

            fixture_date = parse_datetime(match.get('utcDate', ''))
            if not fixture_date:
                continue

            full_time = score.get('fullTime', {})
            status = STATUS_MAP.get(match.get('status', 'SCHEDULED'), 'NS')
            matchday = match.get('matchday')

            Fixture.objects.update_or_create(
                api_id=match_id,
                defaults={
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'fixture_date': fixture_date,
                    'status': status,
                    'home_score': full_time.get('home'),
                    'away_score': full_time.get('away'),
                    'venue': '',
                    'round': str(matchday) if matchday else '',
                }
            )
            count += 1

        return count

    def update_fixture_result(self, fixture_api_id: int) -> bool:
        """Update the result and score of a specific fixture."""
        from apps.fixtures.models import Fixture

        data = self._get(f'matches/{fixture_api_id}', cache_ttl=60)
        if not data:
            return False

        score = data.get('score', {})
        full_time = score.get('fullTime', {})
        status = STATUS_MAP.get(data.get('status', 'SCHEDULED'), 'NS')

        Fixture.objects.filter(api_id=fixture_api_id).update(
            status=status,
            home_score=full_time.get('home'),
            away_score=full_time.get('away'),
        )
        return True

    # -----------------------------------------------------------------------
    # Standings
    # -----------------------------------------------------------------------

    def sync_standings(self) -> int:
        """
        Fetch and upsert standings for every supported competition.
        One request per competition (football-data.org rate limit: 10 req/min).
        """
        import time
        from apps.leagues.models import League
        from apps.teams.models import Team
        from apps.statistics.models import Standing

        count = 0
        league_qs = League.objects.filter(api_id__in=self.SUPPORTED_LEAGUE_IDS)
        comp_code_map = {v: k for k, v in settings.SUPPORTED_COMPETITIONS.items()}

        for league in league_qs:
            # Find the competition code for this league id
            comp_code = None
            for code, comp_id in settings.SUPPORTED_LEAGUES.items():
                if comp_id == league.api_id:
                    comp_code = settings.SUPPORTED_COMPETITIONS.get(code)
                    break
            if not comp_code:
                continue

            data = self._get(
                f'competitions/{comp_code}/standings',
                cache_ttl=settings.API_CACHE_TTL_MEDIUM,
            )
            time.sleep(6)  # stay under 10 req/min

            if not data:
                continue

            season_year = league.season

            for group in data.get('standings', []):
                if group.get('type') != 'TOTAL':
                    continue
                for row in group.get('table', []):
                    team_data = row.get('team', {})
                    team_id = team_data.get('id')
                    if not team_id:
                        continue

                    team, _ = Team.objects.get_or_create(
                        api_id=team_id,
                        defaults={
                            'name': team_data.get('name', ''),
                            'logo': team_data.get('crest', ''),
                        }
                    )

                    gd = row.get('goalDifference', 0) or (
                        (row.get('goalsFor') or 0) - (row.get('goalsAgainst') or 0)
                    )

                    Standing.objects.update_or_create(
                        team=team,
                        league=league,
                        season=season_year,
                        defaults={
                            'position': row.get('position', 0),
                            'points': row.get('points', 0),
                            'played': row.get('playedGames', 0),
                            'wins': row.get('won', 0),
                            'draws': row.get('draw', 0),
                            'losses': row.get('lost', 0),
                            'goals_for': row.get('goalsFor', 0),
                            'goals_against': row.get('goalsAgainst', 0),
                            'goal_difference': gd,
                        }
                    )
                    count += 1

            logger.info(f'Synced standings for {league.name}')

        return count

    # -----------------------------------------------------------------------
    # Team Statistics — computed from DB fixtures (no API needed)
    # -----------------------------------------------------------------------

    def compute_team_statistics(self, season: int = None) -> int:
        """
        Calculate TeamStatistics for every team that has finished fixtures.
        Uses data already in the DB — no API call required.
        Groups by (team, league) and uses each league's own season year.
        """
        from django.db.models import Q
        from apps.fixtures.models import Fixture
        from apps.teams.models import Team
        from apps.leagues.models import League
        from apps.statistics.models import TeamStatistics

        finished_qs = Fixture.objects.filter(
            status='FT',
            home_score__isnull=False,
            away_score__isnull=False,
        ).select_related('home_team', 'away_team', 'league')

        # Collect unique (team, league) pairs
        pairs = set()
        for f in finished_qs:
            pairs.add((f.home_team_id, f.league_id))
            pairs.add((f.away_team_id, f.league_id))

        count = 0
        for team_id, league_id in pairs:
            team_fixtures = finished_qs.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id),
                league_id=league_id,
            ).order_by('-fixture_date')

            total = team_fixtures.count()
            if total == 0:
                continue

            goals_scored = []
            goals_conceded = []
            home_scored = []
            home_conceded = []
            away_scored = []
            away_conceded = []
            btts = 0
            over25 = 0
            over15 = 0
            clean_sheets = 0
            failed_to_score = 0
            last5_wins = last5_draws = last5_losses = 0

            for idx, f in enumerate(team_fixtures):
                is_home = (f.home_team_id == team_id)
                scored = f.home_score if is_home else f.away_score
                conceded = f.away_score if is_home else f.home_score
                total_goals = f.home_score + f.away_score

                goals_scored.append(scored)
                goals_conceded.append(conceded)

                if is_home:
                    home_scored.append(scored)
                    home_conceded.append(conceded)
                else:
                    away_scored.append(scored)
                    away_conceded.append(conceded)

                if scored > 0 and conceded > 0:
                    btts += 1
                if total_goals > 2.5:
                    over25 += 1
                if total_goals > 1.5:
                    over15 += 1
                if conceded == 0:
                    clean_sheets += 1
                if scored == 0:
                    failed_to_score += 1

                if idx < 5:
                    if scored > conceded:
                        last5_wins += 1
                    elif scored == conceded:
                        last5_draws += 1
                    else:
                        last5_losses += 1

            def avg(lst):
                return round(sum(lst) / len(lst), 2) if lst else 0

            def rate(n):
                return round(n / total * 100, 2)

            try:
                team_obj = Team.objects.get(pk=team_id)
                league_obj = League.objects.get(pk=league_id)
            except (Team.DoesNotExist, League.DoesNotExist):
                continue

            # Use the league's own season year (BSA=2026, PL=2025, etc.)
            league_season = season if season is not None else league_obj.season

            TeamStatistics.objects.update_or_create(
                team=team_obj,
                league=league_obj,
                season=league_season,
                defaults={
                    'last_5_wins': last5_wins,
                    'last_5_draws': last5_draws,
                    'last_5_losses': last5_losses,
                    'avg_goals_scored': avg(goals_scored),
                    'avg_goals_conceded': avg(goals_conceded),
                    'both_teams_score_rate': rate(btts),
                    'over25_rate': rate(over25),
                    'over15_rate': rate(over15),
                    'clean_sheet_rate': rate(clean_sheets),
                    'fail_to_score_rate': rate(failed_to_score),
                    'home_avg_goals_scored': avg(home_scored),
                    'home_avg_goals_conceded': avg(home_conceded),
                    'away_avg_goals_scored': avg(away_scored),
                    'away_avg_goals_conceded': avg(away_conceded),
                }
            )
            count += 1

        logger.info(f'Computed statistics for {count} team/league pairs')
        return count

    def sync_team_statistics(self, team_api_id: int, league_api_id: int, season: int = 2025) -> bool:
        """Alias kept for backward compatibility — delegates to compute_team_statistics."""
        self.compute_team_statistics(season=season)
        return True
