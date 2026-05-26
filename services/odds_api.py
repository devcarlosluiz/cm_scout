"""
The Odds API Service (the-odds-api.com v4)
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


class OddsAPIService:
    """
    Wraps The Odds API v4.
    Fetches odds from multiple bookmakers and stores them with history.
    """

    BASE_URL = settings.THE_ODDS_API_BASE_URL

    SPORT_KEYS = {
        'soccer_epl': 'Premier League',
        'soccer_efl_champ': 'Championship',
        'soccer_spain_la_liga': 'La Liga',
        'soccer_germany_bundesliga': 'Bundesliga',
        'soccer_italy_serie_a': 'Serie A',
        'soccer_france_ligue_one': 'Ligue 1',
        'soccer_uefa_champs_league': 'Champions League',
        'soccer_uefa_europa_league': 'Europa League',
        'soccer_brazil_campeonato': 'Brasileirão Série A',
    }

    MARKETS = ['h2h', 'totals', 'btts']

    def __init__(self):
        self.session = requests.Session()
        self.api_key = settings.THE_ODDS_API_KEY

    def _get(self, endpoint: str, params: dict = None, cache_ttl: int = None) -> Optional[dict]:
        params = params or {}
        params['apiKey'] = self.api_key
        cache_key = self._build_cache_key(endpoint, {k: v for k, v in params.items() if k != 'apiKey'})

        if cache_ttl is None:
            cache_ttl = settings.API_CACHE_TTL_SHORT

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        url = f'{self.BASE_URL}/{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            cache.set(cache_key, data, cache_ttl)
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f'OddsAPI error for {endpoint}: {e}')
            return None

    def _build_cache_key(self, endpoint: str, params: dict) -> str:
        key_data = f'odds:{endpoint}:{json.dumps(params, sort_keys=True)}'
        return f'odds_api:{hashlib.md5(key_data.encode()).hexdigest()}'

    def sync_upcoming_odds(self) -> int:
        """Fetch odds for all supported sports and store them."""
        total = 0
        for sport_key in self.SPORT_KEYS:
            count = self._sync_sport_odds(sport_key)
            total += count
        return total

    def _sync_sport_odds(self, sport_key: str) -> int:
        """Fetch and store odds for a single sport."""
        from apps.fixtures.models import Fixture
        from apps.odds.models import Bookmaker, Odd
        from django.utils import timezone
        from datetime import timedelta

        data = self._get(f'sports/{sport_key}/odds', params={
            'regions': 'eu',
            'markets': ','.join(self.MARKETS),
            'oddsFormat': 'decimal',
            'dateFormat': 'iso',
        })

        if not data:
            return 0

        count = 0
        for event in data:
            # Try to match fixture by team names + date
            commence_time = event.get('commence_time', '')
            home_team_name = event.get('home_team', '')
            away_team_name = event.get('away_team', '')

            # Simple name-based matching (production would use a more robust approach)
            fixture = Fixture.objects.filter(
                home_team__name__icontains=home_team_name[:10],
                away_team__name__icontains=away_team_name[:10],
                fixture_date__gte=timezone.now() - timedelta(hours=6),
            ).first()

            if not fixture:
                continue

            for bookmaker_data in event.get('bookmakers', []):
                bookmaker, _ = Bookmaker.objects.get_or_create(
                    name=bookmaker_data.get('title', 'Unknown'),
                )

                for market in bookmaker_data.get('markets', []):
                    market_key = market.get('key', '')
                    market_code = self._map_market(market_key)

                    for outcome in market.get('outcomes', []):
                        Odd.objects.create(
                            fixture=fixture,
                            bookmaker=bookmaker,
                            market=market_code,
                            selection=outcome.get('name', ''),
                            odd=outcome.get('price', 0),
                        )
                        count += 1

        return count

    def _map_market(self, api_market: str) -> str:
        """Map The Odds API market key to internal market code."""
        mapping = {
            'h2h': '1X2',
            'totals': 'OVER_25',
            'btts': 'BTTS',
            'spreads': 'AH',
        }
        return mapping.get(api_market, api_market.upper())
