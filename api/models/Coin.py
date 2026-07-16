from .Model import Model

from sqlmodel import Field

class Coin(Model, table=True):
    __tablename__ = "coin"

    id: str = Field(primary_key=True)
    symbol: str
    name: str
    market_cap: int
    exchange: str
    enabled: bool = Field(default=False)
    score: float = Field(default=0.0)
    
