from sqlmodel import Session, select
from sqlalchemy.sql import func, desc

from .database import engine
from models.Coin import Coin

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