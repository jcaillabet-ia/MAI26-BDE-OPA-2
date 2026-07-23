from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

import ccxt
import pandas as pd


class OHLCVIngestionError(RuntimeError):
    """Erreur côté ingestion OHLCV."""


@dataclass
class CcxtOHLCVClient:
    """
   Pour récupérer des bougies OHLCV.

    """

    exchange_id: str
    enable_rate_limit: bool = True
    exchange: Any = field(init=False)

    def __post_init__(self) -> None:
        # ccxt.binance(), ccxt.coinbase(), etc.
        exchange_class = getattr(ccxt, self.exchange_id, None)

        if exchange_class is None:
            raise OHLCVIngestionError(f"Exchange inconnu dans CCXT: {self.exchange_id}")

        self.exchange = exchange_class(
            {
                "enableRateLimit": self.enable_rate_limit,
            }
        )

    def load_markets(self) -> dict[str, Any]:
        """Charge les marchés disponibles sur l'exchange."""
        try:
            return self.exchange.load_markets()
        except Exception as exc:
            raise OHLCVIngestionError(
                f"Impossible de charger les marchés pour {self.exchange_id}"
            ) from exc

    def supports_ohlcv(self) -> bool:
        """Vérifie si l'exchange sait fournir des bougies OHLCV."""
        return bool(self.exchange.has.get("fetchOHLCV"))

    def symbol_exists(self, symbol: str) -> bool:
        """
        Vérifie si une paire existe sur l'exchange.

        Exemple de symbol CCXT :
        BTC/USDT
        ETH/USD
        """
        markets = self.load_markets()
        return symbol in markets

    def fetch_ohlcv_page(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | None = None,
        limit: int = 1000,
    ) -> list[list[Any]]:
        """
        Récupère une page OHLCV.

        Attention : cette fonction ne fait pas encore la boucle complète.
        Elle récupère juste un paquet de bougies.
        """
        if not self.supports_ohlcv():
            raise OHLCVIngestionError(
                f"{self.exchange_id} ne supporte pas fetch_ohlcv"
            )

        if limit <= 0:
            raise ValueError("limit doit être strictement positif")

        if not self.symbol_exists(symbol):
            raise OHLCVIngestionError(
                f"Symbole indisponible sur {self.exchange_id}: {symbol}"
            )

        time.sleep(0.5)

        try:
            return self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=limit,
            )
        except ccxt.RequestTimeout:
            return None
        except Exception as exc:
            raise OHLCVIngestionError(
                f"Erreur pendant fetch_ohlcv sur {self.exchange_id} / {symbol}"
            ) from exc

    @staticmethod
    def ohlcv_to_dataframe(
        ohlcv: list[list[Any]],
        exchange_id: str,
        symbol: str,
        timeframe: str,
    ) -> pd.DataFrame:
        """Convertit les OHLCV CCXT en DataFrame exploitable."""
        columns = ["timestamp", "open", "high", "low", "close", "volume"]

        df = pd.DataFrame(ohlcv, columns=columns)

        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df["exchange"] = exchange_id
        df["symbol"] = symbol
        df["timeframe"] = timeframe

        numeric_columns = ["open", "high", "low", "close", "volume"]

        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column])

        return df[
            [
                "timestamp",
                "datetime",
                "exchange",
                "symbol",
                "timeframe",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ]
    def timeframe_to_milliseconds(self, timeframe: str) -> int:
        """
        Convertit un timeframe CCXT en millisecondes.

        Exemple :
        1h -> 3600000
        """
        try:
            return int(self.exchange.parse_timeframe(timeframe) * 1000)
        except Exception as exc:
            raise OHLCVIngestionError(f"Timeframe invalide: {timeframe}") from exc

    def fetch_ohlcv_points(
        self,
        symbol: str,
        timeframe: str = "1h",
        n_points: int = 1000,
        since: int | None = None,
        limit_per_request: int = 1000,
    ) -> list[list[Any]]:
        """
        Récupère plusieurs pages OHLCV pour obtenir environ n_points bougies.

        Si since est None, on part d'une date approximative dans le passé.
        C'est utile pour récupérer les dernières bougies disponibles.
        """
        if n_points <= 0:
            raise ValueError("n_points doit être strictement positif")

        if limit_per_request <= 0:
            raise ValueError("limit_per_request doit être strictement positif")

        timeframe_ms = self.timeframe_to_milliseconds(timeframe)

        # Si aucune date de départ n'est donnée, on remonte assez loin
        # pour demander environ n_points bougies.
        current_since = since
        if current_since is None:
            current_since = self.exchange.milliseconds() - (n_points * timeframe_ms)

        all_rows: list[list[Any]] = []
        last_seen_timestamp: int | None = None

        while len(all_rows) < n_points:
            remaining = n_points - len(all_rows)
            current_limit = min(remaining, limit_per_request)

            page = self.fetch_ohlcv_page(
                symbol=symbol,
                timeframe=timeframe,
                since=current_since,
                limit=current_limit,
            )

            if not page:
                break

            all_rows.extend(page)

            new_last_timestamp = page[-1][0]

            # Sécurité pour éviter une boucle infinie si l'exchange renvoie
            # toujours la même dernière bougie.
            if new_last_timestamp == last_seen_timestamp:
                break

            last_seen_timestamp = new_last_timestamp
            current_since = new_last_timestamp + timeframe_ms

            # Si l'exchange renvoie moins que demandé, il n'a probablement
            # plus assez de données à fournir sur cette plage.
            if len(page) < current_limit:
                break

        # Déduplication par timestamp, puis tri chronologique.
        rows_by_timestamp = {row[0]: row for row in all_rows}
        sorted_rows = [rows_by_timestamp[timestamp] for timestamp in sorted(rows_by_timestamp)]

        return sorted_rows[-n_points:]