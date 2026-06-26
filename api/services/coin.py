from sqlmodel import Session, select
from sqlalchemy.sql import func, desc

from .database import engine
from models import Coin, CoinTicker, Ticker

def list_coins() -> list[Coin]:
    with Session(engine) as session:
        statement = select(Coin).order_by(Coin.market_cap.desc()).limit(250)
        rows = session.exec(statement).all()
        coins = [dict(row) for row in rows]

        statement = (
            select(
                Ticker.name
            )
            .join(CoinTicker, Ticker.id == CoinTicker.ticker_id)
            .group_by(Ticker.name)
            .order_by(desc(func.count(CoinTicker.coin_id)))
        )

        tickers = session.exec(statement).all()

        for coin in coins:
            row = list(filter(lambda row: row.id == coin['id'], rows))
            coin_tickers = list(map(lambda row: row.name, row[0].tickers))

            for ticker in tickers:
                if ticker in coin_tickers:
                    coin['ticker'] = ticker
                    break

        return coins

def enable_coin(coin_id: str) -> Coin:
    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()
        coin.enabled = True
        coin.save(session)
        return coin