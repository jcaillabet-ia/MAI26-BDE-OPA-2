from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from .CoinTicker import CoinTicker

if TYPE_CHECKING:
    from .coin import Coin

from .Model import Model

class Ticker(Model, table=True):
    __tablename__ = "ticker"

    id: str = Field(primary_key=True)
    name: str
    base: str
    target: str

    # Relation Many-to-Many avec Coin
    coins: List["Coin"] = Relationship(back_populates="tickers", link_model=CoinTicker)
