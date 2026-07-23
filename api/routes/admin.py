from cassandra.cluster import Session as CassandraSession
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from models.Coin import Coin
from services.clients import build_dict
from services.coin import insert_coins
import services.database as db
from dependencies import get_cassandra

router = APIRouter()

@router.post("/postgres/empty")
def empty_postgres():
    db.run_postgres_script("empty_postgres.sql")

@router.post("/cassandra/empty")
def empty_cassandra(session: CassandraSession = Depends(get_cassandra)):
    db.run_cassandra_script("empty_cassandra.cql", session)

@router.post("/postgres/fill", status_code=status.HTTP_204_NO_CONTENT)
def fill_postgres():
    """
    Recupère la liste des monnaies gérables, et les insère dans la base de données PostgreSQL
    """

    entries = build_dict()
    insert_coins(entries)

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