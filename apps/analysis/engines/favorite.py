from typing import Optional
from .base import BaseEngine, AnalysisResult


class FavoriteEngine(BaseEngine):
    """
    Scores the Match Winner (Favorite Wins) market.

    Scoring:
    +25 if favorite has significantly better position
    +20 if home team win rate > 55%
    +15 if favorite's recent form is W/W/W/D
    +10 if favorite scores avg > 1.5
    +10 if underdog concedes avg > 1.5
    +5  if H2H advantage > 60%
    -15 if teams are in similar form
    """
    market_name = 'Favorito Vence'
    market_code = '1X2'

    def calculate(self, fixture, home_stats=None, away_stats=None, h2h=None) -> Optional[AnalysisResult]:
        if not home_stats or not away_stats:
            return None

        from apps.statistics.models import Standing

        score = 0
        reasons = []
        details = {}

        home_standing = Standing.objects.filter(
            team=fixture.home_team, league=fixture.league
        ).first()
        away_standing = Standing.objects.filter(
            team=fixture.away_team, league=fixture.league
        ).first()

        # Position advantage
        if home_standing and away_standing:
            pos_diff = away_standing.position - home_standing.position
            details['home_position'] = home_standing.position
            details['away_position'] = away_standing.position

            if pos_diff >= 5:
                score += 25
                reasons.append(
                    f'{fixture.home_team.name} está {pos_diff} posições acima na tabela'
                )
            elif pos_diff >= 2:
                score += 15
                reasons.append(
                    f'{fixture.home_team.name} tem vantagem na tabela'
                )

            home_wr = home_standing.win_rate
            details['home_win_rate'] = home_wr
            if home_wr > 55:
                score += 20
                reasons.append(f'{fixture.home_team.name} vence {home_wr:.0f}% em casa')

        # Form advantage
        home_wins = home_stats.last_5_wins
        home_losses = home_stats.last_5_losses
        away_wins = away_stats.last_5_wins
        away_losses = away_stats.last_5_losses

        details['home_last5'] = {'W': home_wins, 'L': home_losses}
        details['away_last5'] = {'W': away_wins, 'L': away_losses}

        if home_wins >= 3 and home_losses == 0:
            score += 15
            reasons.append(f'{fixture.home_team.name} em excelente forma recente')
        elif home_wins >= 2:
            score += 10
            reasons.append(f'{fixture.home_team.name} em boa forma recente')

        # Scoring power vs defensive weakness
        home_avg = float(home_stats.avg_goals_scored)
        away_conceded = float(away_stats.avg_goals_conceded)

        if home_avg > 1.5:
            score += 10
            reasons.append(f'{fixture.home_team.name} marca {home_avg:.2f}/jogo')
        if away_conceded > 1.5:
            score += 10
            reasons.append(f'{fixture.away_team.name} sofre {away_conceded:.2f}/jogo')

        # H2H advantage
        if h2h and h2h.count() >= 3:
            home_wins_h2h = sum(
                1 for f in h2h
                if f.home_score is not None and f.away_score is not None
                and (
                    (f.home_team_id == fixture.home_team_id and f.home_score > f.away_score) or
                    (f.away_team_id == fixture.home_team_id and f.away_score > f.home_score)
                )
            )
            h2h_rate = home_wins_h2h / h2h.count() * 100
            details['h2h_home_win_rate'] = round(h2h_rate, 1)
            if h2h_rate > 60:
                score += 5
                reasons.append(f'H2H favorável: {h2h_rate:.0f}%')

        # Penalty if similar form
        if abs(home_wins - away_wins) <= 1 and abs(home_losses - away_losses) <= 1:
            score -= 15

        score = self._clamp(score)
        probability = min(score / 100, 0.92)

        return AnalysisResult(
            score=score,
            probability=probability,
            reason=' | '.join(reasons) if reasons else 'Equilíbrio entre as equipes',
            market=self.market_code,
            details=details,
        )
