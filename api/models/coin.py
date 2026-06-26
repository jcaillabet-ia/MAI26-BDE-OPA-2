from typing import List
from sqlmodel import Field, Relationship
from .CoinTicker import CoinTicker

from .Model import Model

class Coin(Model, table=True):
    __tablename__ = "coin"

    id: str = Field(primary_key=True)
    symbol: str
    name: str
    market_cap: int
    enabled: bool = Field(default=False)

    # Relation Many-to-Many avec Ticker
    tickers: List["Ticker"] = Relationship(back_populates="coins", link_model=CoinTicker)
