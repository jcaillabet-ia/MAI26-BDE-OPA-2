from database import open_connection
from coingecko import build_dict

from models.Coin import Coin
from sqlmodel import select, Session, create_engine

import os
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

session = next(get_session())

def main():
    exchange_dict = build_dict()

    for entry in exchange_dict:
        statement = select(Coin).where(Coin.id == entry['id'])
        row = session.execute(statement).first()

        if not row:
            coin = Coin()
            coin.id=entry['id']
            coin.symbol=entry['symbol'] 
            coin.name=entry['name'] 
            coin.market_cap=entry['market_cap'] 
            coin.enabled=False 
            coin.ticker=entry['exchange']
            coin.save(session)
  
if __name__ == "__main__":
    main()
