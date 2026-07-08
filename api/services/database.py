import os
from sqlmodel import Session, create_engine

from cassandra.cluster import Cluster

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def open_script_file(script_name):
    schema_path = os.path.join(os.path.dirname(__file__), "../scripts/" + script_name)
    with open(schema_path, "r") as schema_file:
        return schema_file.read()

def open_postgres_connection():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
    return psycopg2.connect(database_url, connect_timeout=5)

def run_postgres_script(script_name):
    conn = open_postgres_connection()
    cursor = conn.cursor()

    sql = open_script_file(script_name)

    cursor.execute(sql)
    conn.commit()

def open_cassandra_connection():
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    cluster = Cluster(CLUSTER_IPS)
    return cluster.connect()

def run_cassandra_script(script_name):
    conn = open_cassandra_connection()

    sql = open_script_file(script_name)
    queries = sql.split(';')

    for query in queries:
        query_clean = query.strip() 
        if query_clean:
            conn.execute(query_clean)

def save_cassandra_candles(candles):
    conn = open_cassandra_connection()
    cursor = conn.cursor()
    for candle in candles:
        cursor.execute("INSERT INTO candles (symbol, timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)", (candle['symbol'], candle['timestamp'], candle['open'], candle['high'], candle['low'], candle['close'], candle['volume']))
    conn.commit()
    