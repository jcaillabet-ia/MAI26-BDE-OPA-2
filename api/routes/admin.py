from fastapi import APIRouter, Depends
from sqlmodel import Session
from cassandra.cluster import Session as CassandraSession

from models.Coin import Coin
from services.clients import build_dict
import services.database as db
from dependencies import get_cassandra

router = APIRouter()

@router.post("/postgres/empty")
def empty_postgres():
    db.run_postgres_script("empty_postgres.sql")

@router.post("/cassandra/empty")
def empty_cassandra(session: CassandraSession = Depends(get_cassandra)):
    db.run_cassandra_script("empty_cassandra.cql", session)

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

# @router.post("/postgres/clear")
# def clear_postgres():
#     db.run_postgres_script("clear_postgres.sql")

# @router.post("/cassandra/clear")
# def clear_cassandra():
#     db.run_cassandra_script("clear_cassandra.cql")

# @router.post("/postgres/init")
# def init_postgres():
#     db.run_postgres_script("schema_postgres.sql")

# @router.post("/cassandra/init")
# def init_cassandra():
#     db.run_cassandra_script("schema_cassandra.cql")