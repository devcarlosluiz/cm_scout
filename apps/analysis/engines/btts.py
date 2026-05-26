from typing import Optional
from .base import BaseEngine, AnalysisResult


class BTTSEngine(BaseEngine):
    """
    Scores the Both Teams to Score (BTTS - Ambas Marcam) market.

    Scoring:
    +25 if both teams BTTS rate > 65%
    +15 if avg BTTS > 60%
    +10 if home team scores > 1.2 avg
    +10 if away team scores > 0.9 avg
    +10 if home team concedes > 1.0 avg
    +10 if away team concedes > 1.2 avg
    +5  if H2H BTTS > 60%
    -15 if either team has fail_to_score_rate > 40%
    -10 if either team has clean_sheet_rate > 50%
    """
    market_name = 'Ambas Marcam'
    market_code = 'BTTS'

    def calculate(self, fixture, home_stats=None, away_stats=None, h2h=None) -> Optional[AnalysisResult]:
        if not home_stats or not away_stats:
            return None

        score = 0
        reasons = []
        details = {}

        home_btts = float(home_stats.both_teams_score_rate)
        away_btts = float(away_stats.both_teams_score_rate)
        avg_btts = (home_btts + away_btts) / 2
        details['home_btts'] = home_btts
        details['away_btts'] = away_btts
        details['avg_btts'] = round(avg_btts, 1)

        if home_btts > 65 and away_btts > 65:
            score += 25
            reasons.append(f'Ambos com BTTS alto (Casa:{home_btts:.0f}%, Fora:{away_btts:.0f}%)')
        elif avg_btts > 60:
            score += 15
            reasons.append(f'BTTS médio: {avg_btts:.0f}%')

        home_avg_scored = float(home_stats.avg_goals_scored)
        away_avg_scored = float(away_stats.avg_goals_scored)
        home_avg_conceded = float(home_stats.avg_goals_conceded)
        away_avg_conceded = float(away_stats.avg_goals_conceded)

        details['home_avg_scored'] = home_avg_scored
        details['away_avg_scored'] = away_avg_scored

        if home_avg_scored > 1.2:
            score += 10
            reasons.append(f'{fixture.home_team.name} marca {home_avg_scored:.2f}/jogo')
        if away_avg_scored > 0.9:
            score += 10
            reasons.append(f'{fixture.away_team.name} marca {away_avg_scored:.2f}/jogo')
        if home_avg_conceded > 1.0:
            score += 10
            reasons.append(f'{fixture.home_team.name} sofre {home_avg_conceded:.2f}/jogo')
        if away_avg_conceded > 1.2:
            score += 10
            reasons.append(f'{fixture.away_team.name} sofre {away_avg_conceded:.2f}/jogo')

        if h2h and h2h.count() >= 3:
            btts_count = sum(
                1 for f in h2h
                if f.home_score is not None and f.away_score is not None
                and f.home_score > 0 and f.away_score > 0
            )
            h2h_btts = btts_count / h2h.count() * 100
            details['h2h_btts'] = round(h2h_btts, 1)
            if h2h_btts > 60:
                score += 5
                reasons.append(f'H2H BTTS: {h2h_btts:.0f}%')

        home_fts = float(home_stats.fail_to_score_rate)
        away_fts = float(away_stats.fail_to_score_rate)
        if home_fts > 40:
            score -= 15
            reasons.append(f'{fixture.home_team.name} não marca em {home_fts:.0f}% dos jogos')
        if away_fts > 40:
            score -= 15
            reasons.append(f'{fixture.away_team.name} não marca em {away_fts:.0f}% dos jogos')

        home_cs = float(home_stats.clean_sheet_rate)
        away_cs = float(away_stats.clean_sheet_rate)
        if home_cs > 50 or away_cs > 50:
            score -= 10

        score = self._clamp(score)
        probability = min(score / 100, 0.95)

        return AnalysisResult(
            score=score,
            probability=probability,
            reason=' | '.join(reasons) if reasons else 'Dados insuficientes',
            market=self.market_code,
            details=details,
        )
