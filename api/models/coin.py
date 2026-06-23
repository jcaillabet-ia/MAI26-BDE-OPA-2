from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .coin_ticker import CoinTicker

if TYPE_CHECKING:
    from .ticker import Ticker

class Coin(SQLModel, table=True):
    __tablename__ = "coin"

    id: str = Field(primary_key=True)
    symbol: str
    name: str
    market_cap: int
    enabled: bool = Field(default=False)

    # Relation Many-to-Many avec Ticker
    tickers: List["Ticker"] = Relationship(back_populates="coins", link_model=CoinTicker)
