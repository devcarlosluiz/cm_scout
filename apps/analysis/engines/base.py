from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalysisResult:
    """Represents the result of a market analysis."""
    score: int
    probability: float
    reason: str
    market: str
    details: dict = field(default_factory=dict)

    @property
    def confidence(self) -> str:
        if self.score <= 30:
            return 'low'
        elif self.score <= 60:
            return 'medium'
        return 'high'

    @property
    def confidence_label(self) -> str:
        return {'low': 'Baixa', 'medium': 'Média', 'high': 'Alta'}.get(self.confidence, '')

    @property
    def is_recommended(self) -> bool:
        return self.score >= 61


class BaseEngine(ABC):
    """
    Abstract base for all analysis engines.
    Implements the Strategy Pattern — each subclass defines its own
    scoring algorithm for a specific betting market.
    """
    market_name: str = ''
    market_code: str = ''

    @abstractmethod
    def calculate(self, fixture, home_stats=None, away_stats=None, h2h=None) -> Optional[AnalysisResult]:
        """
        Calculate market score for the given fixture.

        Args:
            fixture: Fixture model instance
            home_stats: TeamStatistics for home team
            away_stats: TeamStatistics for away team
            h2h: QuerySet of last 5 head-to-head fixtures

        Returns:
            AnalysisResult or None if insufficient data
        """
        pass

    def _clamp(self, value: int, min_val: int = 0, max_val: int = 100) -> int:
        return max(min_val, min(max_val, value))
