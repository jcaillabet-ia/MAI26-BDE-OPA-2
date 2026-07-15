from .Model import Model

from sqlmodel import Field

class Coin(Model, table=True):
    __tablename__ = "coin"

    id: str = Field(primary_key=True) # id coingecko
    symbol: str # symmbole de l'exchange
    name: str # name coingecko
    market_cap: int # market cap coingecko
    enabled: bool = Field(default=False) # API
    ticker: str # ticker ccxt
