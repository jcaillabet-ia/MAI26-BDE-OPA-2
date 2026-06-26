from sqlmodel import Field

from .Model import Model

class CoinTicker(Model, table=True):
    __tablename__ = "coin_ticker"

    coin_id: str = Field(foreign_key="coin.id", primary_key=True)
    ticker_id: str = Field(foreign_key="ticker.id", primary_key=True)
