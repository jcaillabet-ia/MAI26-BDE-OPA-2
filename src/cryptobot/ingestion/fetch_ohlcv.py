from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from cryptobot.ingestion.ccxt_ohlcv_client import CcxtOHLCVClient
from cryptobot.ingestion.exchange_resolver import resolve_market


DEFAULT_EXCHANGE_PRIORITY = ["binance", "coinbase", "kraken"]
DEFAULT_QUOTE_PRIORITY = ["USDT", "USD", "USDC"]


def fetch_asset_ohlcv(
    asset: str,
    n_points: int,
    timeframe: str = "1h",
    exchange_priority: list[str] | None = None,
    quote_priority: list[str] | None = None,
    limit_per_request: int = 1000,
) -> pd.DataFrame:
    """
    Fonction générale d'ingestion OHLCV.

    On donne un asset, ex: BTC.
    La fonction trouve où le récupérer, puis récupère n_points bougies.
    """
    if n_points <= 0:
        raise ValueError("n_points doit être strictement positif")

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

    # On garde la trace de la source choisie par le resolver
    df["base_asset"] = market.base_asset
    df["quote_asset"] = market.quote_asset
    df["source_priority_rank"] = market.priority_rank

    return df


def save_sample_json(df: pd.DataFrame, output_path: str | Path) -> None:
    """
    Sauvegarde un petit exemple JSON exploitable pour le rapport.
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Récupère des données OHLCV via CCXT avec priorité d'exchanges."
    )

    parser.add_argument("--asset", default="BTC", help="Crypto à récupérer, ex: BTC")
    parser.add_argument("--timeframe", default="1h", help="Timeframe OHLCV, ex: 1h")
    parser.add_argument("--n-points", type=int, default=100, help="Nombre de bougies")
    parser.add_argument(
        "--limit-per-request",
        type=int,
        default=1000,
        help="Nombre max demandé par appel CCXT",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Chemin optionnel pour sauvegarder un JSON d'exemple",
    )

    args = parser.parse_args()

    df = fetch_asset_ohlcv(
        asset=args.asset,
        timeframe=args.timeframe,
        n_points=args.n_points,
        limit_per_request=args.limit_per_request,
    )

    print("Ingestion terminée")
    print("Nombre de lignes :", len(df))
    print("Exchange utilisé :", df["exchange"].iloc[0])
    print("Symbol utilisé :", df["symbol"].iloc[0])
    print("Quote utilisée :", df["quote_asset"].iloc[0])
    print("Priority rank :", df["source_priority_rank"].iloc[0])
    print()
    print(df.head())
    print()
    print(df.tail())

    if args.output:
        save_sample_json(df, args.output)
        print()
        print(f"JSON sauvegardé dans : {args.output}")


if __name__ == "__main__":
    main()