from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .coin_ticker import CoinTicker

if TYPE_CHECKING:
    from .coin import Coin

class Ticker(SQLModel, table=True):
    __tablename__ = "ticker"

    id: str = Field(primary_key=True)
    name: str
    base: str
    target: str

    # Relation Many-to-Many avec Coin
    coins: List["Coin"] = Relationship(back_populates="tickers", link_model=CoinTicker)
