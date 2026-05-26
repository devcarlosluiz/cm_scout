from typing import Optional
from .base import BaseEngine, AnalysisResult


class Over25Engine(BaseEngine):
    """
    Scores the Over 2.5 Goals market.

    Scoring Criteria:
    +20 if combined avg goals > 2.8
    +15 if BTTS rate > 70%
    +10 if over25 rate > 65%
    +10 if away team scores avg > 1.0
    +10 if home team scores avg > 1.4
    +5  if H2H has > 60% over 2.5 matches
    +10 if both teams over25_rate > 55%
    -10 if either team has clean sheet rate > 60%
    """
    market_name = 'Over 2.5 Gols'
    market_code = 'OVER_25'

    def calculate(self, fixture, home_stats=None, away_stats=None, h2h=None) -> Optional[AnalysisResult]:
        if not home_stats or not away_stats:
            return None

        score = 0
        reasons = []
        details = {}

        home_avg = float(home_stats.avg_goals_scored)
        away_avg = float(away_stats.avg_goals_scored)
        combined_avg = float(home_stats.avg_goals_scored) + float(away_stats.avg_goals_conceded) / 2 + \
                       float(away_stats.avg_goals_scored) + float(home_stats.avg_goals_conceded) / 2
        combined_avg = combined_avg / 2

        details['combined_avg'] = round(combined_avg, 2)

        if combined_avg > 2.8:
            score += 20
            reasons.append(f'Média combinada de gols: {combined_avg:.2f}')

        home_btts = float(home_stats.both_teams_score_rate)
        away_btts = float(away_stats.both_teams_score_rate)
        avg_btts = (home_btts + away_btts) / 2
        details['avg_btts'] = round(avg_btts, 1)

        if avg_btts > 70:
            score += 15
            reasons.append(f'BTTS médio: {avg_btts:.0f}%')

        home_over25 = float(home_stats.over25_rate)
        away_over25 = float(away_stats.over25_rate)
        avg_over25 = (home_over25 + away_over25) / 2
        details['avg_over25'] = round(avg_over25, 1)

        if avg_over25 > 65:
            score += 10
            reasons.append(f'Taxa Over 2.5 média: {avg_over25:.0f}%')

        if home_avg > 1.4:
            score += 10
            reasons.append(f'{fixture.home_team.name} marca {home_avg:.2f} em média')

        if away_avg > 1.0:
            score += 10
            reasons.append(f'{fixture.away_team.name} marca {away_avg:.2f} fora')

        if home_over25 > 55 and away_over25 > 55:
            score += 10
            reasons.append('Ambos têm alta taxa Over 2.5')

        # H2H bonus
        if h2h and h2h.count() >= 3:
            over_count = sum(
                1 for f in h2h
                if f.home_score is not None and f.away_score is not None
                and (f.home_score + f.away_score) > 2
            )
            h2h_rate = over_count / h2h.count() * 100
            details['h2h_over25_rate'] = round(h2h_rate, 1)
            if h2h_rate > 60:
                score += 5
                reasons.append(f'H2H Over 2.5: {h2h_rate:.0f}%')

        # Penalty for defensive teams
        home_cs = float(home_stats.clean_sheet_rate)
        away_cs = float(away_stats.clean_sheet_rate)
        if home_cs > 60 or away_cs > 60:
            score -= 10
            reasons.append('Time com alta taxa de clean sheet')

        score = self._clamp(score)
        probability = min(score / 100, 0.95)

        return AnalysisResult(
            score=score,
            probability=probability,
            reason=' | '.join(reasons) if reasons else 'Dados insuficientes',
            market=self.market_code,
            details=details,
        )
