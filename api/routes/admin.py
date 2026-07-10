from fastapi import APIRouter
from sqlmodel import Session

from models.Coin import Coin
from services.clients import build_dict
import services.database as db

router = APIRouter()

@router.post("/postgres/clear")
def clear_postgres():
    db.run_postgres_script("clear_postgres.sql")

@router.post("/postgres/init")
def init_postgres():
    db.run_postgres_script("schema_postgres.sql")

@router.post("/postgres/fill")
def fill_postgres():
    with Session(db.engine) as session:
        entries = build_dict()
        for entry in entries:
            coin = Coin(
                id=entry['id'],
                name=entry['name'],
                base_asset=entry['base'],
                quote_asset=entry['quote'],
                symbol=entry['symbol'],
                market_cap=entry['market_cap'],
                ticker=entry['exchange']
            )
            coin.save(session)

@router.post("/cassandra/clear")
def clear_cassandra():
    db.run_cassandra_script("clear_cassandra.cql")

@router.post("/cassandra/init")
def init_cassandra():
    db.run_cassandra_script("schema_cassandra.cql")