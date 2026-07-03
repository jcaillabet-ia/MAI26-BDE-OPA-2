from __future__ import annotations

from dataclasses import dataclass

from cryptobot.ingestion.ccxt_ohlcv_client import (
    CcxtOHLCVClient,
    OHLCVIngestionError,
)


@dataclass
class ResolvedMarket:
    exchange_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    priority_rank: int


class MarketResolverError(RuntimeError):
    """Erreur quand aucun marché compatible n'est trouvé."""


def build_candidate_symbols(asset: str, quote_assets: list[str]) -> list[tuple[str, str]]:
    """
    Crée les paires possibles au format CCXT.

    Exemple :
    BTC + [USDT, USD] -> BTC/USDT, BTC/USD
    """
    asset = asset.upper()

    candidates = []

    for quote in quote_assets:
        quote = quote.upper()
        symbol = f"{asset}/{quote}"
        candidates.append((symbol, quote))

    return candidates


def resolve_market(
    asset: str,
    exchange_priority: list[str],
    quote_priority: list[str],
) -> ResolvedMarket:
    """
    Trouve le premier exchange + symbol disponible selon nos priorités.

    On ne récupère pas encore les OHLCV ici.
    On choisit juste la meilleure source disponible.
    """
    base_asset = asset.upper()
    candidate_symbols = build_candidate_symbols(base_asset, quote_priority)

    for rank, exchange_id in enumerate(exchange_priority, start=1):
        try:
            client = CcxtOHLCVClient(exchange_id)

            if not client.supports_ohlcv():
                continue

            markets = client.load_markets()

        except OHLCVIngestionError:
            # Si un exchange plante au chargement, on passe au suivant.
            continue

        for symbol, quote_asset in candidate_symbols:
            if symbol in markets:
                return ResolvedMarket(
                    exchange_id=exchange_id,
                    symbol=symbol,
                    base_asset=base_asset,
                    quote_asset=quote_asset,
                    priority_rank=rank,
                )

    raise MarketResolverError(
        f"Aucun marché OHLCV trouvé pour {base_asset} "
        f"avec exchanges={exchange_priority} et quotes={quote_priority}"
    )