from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from services.clients import build_dict
from ingestion.ccxt_ohlcv_client import (
    CcxtOHLCVClient,
    OHLCVIngestionError,
)
from ingestion.exchange_resolver import (
    MarketResolverError,
    ResolvedMarket,
)


DEFAULT_EXCHANGE_PRIORITY = ["binance", "coinbase", "kraken"]
DEFAULT_QUOTE_PRIORITY = ["USDT", "USD", "USDC"]


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
    Trouve le premier exchange + symbole disponible selon nos priorités.

    Cette fonction ne récupère pas les OHLCV.
    Elle choisit uniquement le marché à interroger.
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


def fetch_asset_ohlcv(
    asset: str,
    n_points: int,
    timeframe: str = "1h",
    exchange_priority: list[str] | None = None,
    quote_priority: list[str] | None = None,
    limit_per_request: int = 1000,
) -> pd.DataFrame:
    """
    Récupère des données OHLCV pour un asset.

    Exemple :
    asset = BTC
    timeframe = 1h
    n_points = 100
    """
    if n_points <= 0:
        raise ValueError("n_points doit être strictement positif")

    market = None
    try:
        dic = build_dict()
        exchange_entry = list(filter(lambda x: x['symbol'].startswith(asset + '/'), dic))[0]
        if exchange_entry:
            market = ResolvedMarket(exchange_id=exchange_entry['exchange'], symbol=exchange_entry['symbol'], base_asset=exchange_entry['base'], quote_asset=exchange_entry['quote'], priority_rank=1)
    except Exception as e:
        print(e)

    if not market:
        exchanges = exchange_priority or DEFAULT_EXCHANGE_PRIORITY
        quotes = quote_priority or DEFAULT_QUOTE_PRIORITY

        market = resolve_market(
            asset=asset,
            exchange_priority=exchanges,
            quote_priority=quotes,
        )

    client = CcxtOHLCVClient(market.exchange_id)

    ohlcv = client.fetch_ohlcv_points(
        symbol=market.symbol,
        timeframe=timeframe,
        n_points=n_points,
        limit_per_request=limit_per_request,
    )

    df = client.ohlcv_to_dataframe(
        ohlcv=ohlcv,
        exchange_id=market.exchange_id,
        symbol=market.symbol,
        timeframe=timeframe,
    )

    df["base_asset"] = market.base_asset
    df["quote_asset"] = market.quote_asset
    df["source_priority_rank"] = market.priority_rank

    return df


def save_sample_json(df: pd.DataFrame, output_path: str | Path) -> None:
    """
    Sauvegarde un exemple JSON exploitable pour le rapport ou les tests.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        raise ValueError("Impossible de sauvegarder un DataFrame vide")

    metadata = {
        "source_type": "ccxt",
        "exchange": df["exchange"].iloc[0],
        "symbol": df["symbol"].iloc[0],
        "base_asset": df["base_asset"].iloc[0],
        "quote_asset": df["quote_asset"].iloc[0],
        "timeframe": df["timeframe"].iloc[0],
        "source_priority_rank": int(df["source_priority_rank"].iloc[0]),
        "rows": len(df),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    records = df.copy()
    records["datetime"] = records["datetime"].astype(str)

    payload = {
        "metadata": metadata,
        "ohlcv": records.to_dict(orient="records"),
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def run_ingestion(
    asset: str = "BTC",
    timeframe: str = "1h",
    n_points: int = 100,
    limit_per_request: int = 1000,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Lance une ingestion complète et retourne un résumé exploitable par l'API.
    """
    df = fetch_asset_ohlcv(
        asset=asset,
        timeframe=timeframe,
        n_points=n_points,
        limit_per_request=limit_per_request,
    )

    if output_path is not None:
        save_sample_json(df, output_path)

    return {
        "status": "success",
        "rows": len(df),
        "exchange": df["exchange"].iloc[0],
        "symbol": df["symbol"].iloc[0],
        "base_asset": df["base_asset"].iloc[0],
        "quote_asset": df["quote_asset"].iloc[0],
        "timeframe": df["timeframe"].iloc[0],
        "source_priority_rank": int(df["source_priority_rank"].iloc[0]),
        "output_path": str(output_path) if output_path is not None else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Récupère des données OHLCV via CCXT."
    )

    parser.add_argument("--asset", default="BTC", help="Crypto à récupérer, ex: BTC")
    parser.add_argument("--timeframe", default="1h", help="Timeframe OHLCV, ex: 1h")
    parser.add_argument("--n-points", type=int, default=100, help="Nombre de bougies")
    parser.add_argument(
        "--limit-per-request",
        type=int,
        default=1000,
        help="Nombre maximal demandé par appel CCXT",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Chemin optionnel pour sauvegarder un JSON d'exemple",
    )

    args = parser.parse_args()

    result = run_ingestion(
        asset=args.asset,
        timeframe=args.timeframe,
        n_points=args.n_points,
        limit_per_request=args.limit_per_request,
        output_path=args.output,
    )

    print("Ingestion terminée")
    print("Nombre de lignes :", result["rows"])
    print("Exchange utilisé :", result["exchange"])
    print("Symbol utilisé :", result["symbol"])
    print("Quote utilisée :", result["quote_asset"])
    print("Priority rank :", result["source_priority_rank"])

    if result["output_path"]:
        print("JSON sauvegardé dans :", result["output_path"])


if __name__ == "__main__":
    main()
