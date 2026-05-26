from .over25 import Over25Engine
from .btts import BTTSEngine
from .favorite import FavoriteEngine
from .handicap import HandicapEngine

__all__ = ['Over25Engine', 'BTTSEngine', 'FavoriteEngine', 'HandicapEngine']

# Registry of all available engines
ENGINE_REGISTRY = {
    'OVER_25': Over25Engine,
    'BTTS': BTTSEngine,
    '1X2': FavoriteEngine,
    'AH': HandicapEngine,
}


def get_all_engines():
    """Return instances of all registered engines."""
    return [cls() for cls in ENGINE_REGISTRY.values()]
