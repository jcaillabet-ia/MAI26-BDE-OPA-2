from sqlmodel import Session, select
from sqlalchemy.sql import func, desc

from .database import engine
from models.Coin import Coin

def insert_coins(catalog: list):
    coins = list_coins()

    with Session(engine) as session:
        for entry in catalog:
            existing_coin = list(filter(lambda x: x['id'] == entry['id'], coins))
            if not existing_coin:
                coin = Coin(
                    id=entry['id'],
                    name=entry['name'],
                    base_asset=entry['base'],
                    quote_asset=entry['quote'],
                    symbol=entry['symbol'],
                    market_cap=entry['market_cap'],
                    exchange=entry['exchange']
                )
                coin.save(session)

def get_coin(coin_id: str) -> Coin:
    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()
        return dict(coin)

def list_coins() -> list[Coin]:
    with Session(engine) as session:
        statement = select(Coin).order_by(Coin.market_cap.desc()).limit(250)
        rows = session.exec(statement).all()
        coins = [dict(row) for row in rows]

        return coins

def enable_coin(coin_id: str) -> Coin:
    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()
        coin.enabled = True
        coin.save(session)
        return coin

def disable_coin(coin_id: str) -> Coin:
    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()
        coin.enabled = False
        coin.save(session)
        return coin