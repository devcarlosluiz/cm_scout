from typing import Optional
from .base import BaseEngine, AnalysisResult


class HandicapEngine(BaseEngine):
    """
    Scores the Asian Handicap market.

    Scoring:
    +25 if home team dominates form (4+ wins in last 5)
    +20 if avg goals difference > 1.0
    +15 if position difference >= 8
    +10 if home scored > 2.0 avg
    +10 if away conceded > 2.0 avg
    -10 if away team also has strong form
    """
    market_name = 'Handicap Asiático'
    market_code = 'AH'

    def calculate(self, fixture, home_stats=None, away_stats=None, h2h=None) -> Optional[AnalysisResult]:
        if not home_stats or not away_stats:
            return None

        score = 0
        reasons = []
        details = {}

        home_wins_last5 = home_stats.last_5_wins
        away_wins_last5 = away_stats.last_5_wins
        form_diff = home_wins_last5 - away_wins_last5

        details['home_last5_wins'] = home_wins_last5
        details['away_last5_wins'] = away_wins_last5

        if home_wins_last5 >= 4:
            score += 25
            reasons.append(f'{fixture.home_team.name} domina a forma recente ({home_wins_last5}/5 vitórias)')

        home_avg = float(home_stats.avg_goals_scored)
        away_conceded = float(away_stats.avg_goals_conceded)
        goal_diff = home_avg - float(away_stats.avg_goals_scored)

        details['goal_diff'] = round(goal_diff, 2)

        if goal_diff > 1.0:
            score += 20
            reasons.append(f'Diferença de gols: {goal_diff:.2f}')
        elif goal_diff > 0.5:
            score += 10

        from apps.statistics.models import Standing
        home_standing = Standing.objects.filter(
            team=fixture.home_team, league=fixture.league
        ).first()
        away_standing = Standing.objects.filter(
            team=fixture.away_team, league=fixture.league
        ).first()

        if home_standing and away_standing:
            pos_diff = away_standing.position - home_standing.position
            details['position_diff'] = pos_diff
            if pos_diff >= 8:
                score += 15
                reasons.append(f'Diferença de {pos_diff} posições na tabela')

        if home_avg > 2.0:
            score += 10
            reasons.append(f'{fixture.home_team.name} marca {home_avg:.2f}/jogo')

        if away_conceded > 2.0:
            score += 10
            reasons.append(f'{fixture.away_team.name} sofre {away_conceded:.2f}/jogo')

        if away_wins_last5 >= 3:
            score -= 10
            reasons.append(f'{fixture.away_team.name} também em boa forma')

        score = self._clamp(score)
        probability = min(score / 100, 0.90)

        return AnalysisResult(
            score=score,
            probability=probability,
            reason=' | '.join(reasons) if reasons else 'Sem vantagem clara',
            market=self.market_code,
            details=details,
        )
