import os
from fastapi import APIRouter

import services.database as db

from services.coin import list_coins, enable_coin, disable_coin

router = APIRouter()

@router.post("/postgres/clear")
def clear_postgres():
    db.run_postgres_script("clear_postgres.sql")

@router.post("/postgres/init")
def init_postgres():
    db.run_postgres_script("schema_postgres.sql")

@router.post("/cassandra/clear")
def clear_cassandra():
    db.run_cassandra_script("clear_cassandra.cql")

@router.post("/cassandra/init")
def init_cassandra():
    db.run_cassandra_script("schema_cassandra.cql")