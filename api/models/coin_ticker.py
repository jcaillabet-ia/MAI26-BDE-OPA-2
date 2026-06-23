from sqlmodel import SQLModel, Field

class CoinTicker(SQLModel, table=True):
    __tablename__ = "coin_ticker"

    coin_id: str = Field(foreign_key="coin.id", primary_key=True)
    ticker_id: str = Field(foreign_key="ticker.id", primary_key=True)
