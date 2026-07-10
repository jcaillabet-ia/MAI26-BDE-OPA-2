from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResolvedMarket:
    """
    Marché retenu après résolution de priorité.

    Exemple :
    asset BTC
    exchange binance
    symbol BTC/USDT
    """

    exchange_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    priority_rank: int


class MarketResolverError(RuntimeError):
    """
    Erreur levée lorsqu'aucun marché compatible n'est trouvé.
    """
