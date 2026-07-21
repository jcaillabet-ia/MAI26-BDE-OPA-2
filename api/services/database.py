from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from cassandra.query import tuple_factory
from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent
from cassandra.query import BatchStatement, ConsistencyLevel, BatchType
from cassandra.query import dict_factory, SimpleStatement
from concurrent.futures import ThreadPoolExecutor
import os
import psycopg2
from sqlmodel import Session, create_engine
from dependencies import get_cassandra
from fastapi import Depends

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

def run_cassandra_script(script_name, session: Session):
    sql = open_script_file(script_name)
    queries = sql.split(';')

    for query in queries:
        query_clean = query.strip() 
        if query_clean:
            session.execute(query_clean)

def save_cassandra_candles(crypto_id, candles, session: Session):

    query = "INSERT INTO candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    prepared = session.prepare(query)

    data_to_insert = []

    for candle in candles:
        date = datetime.fromtimestamp(candle['timestamp'] / 1000.0, tz=timezone.utc)
        bucket_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).date()
        data_to_insert.append((crypto_id, bucket_date, candle['timestamp'], float(candle['open']), float(candle['high']), float(candle['low']), float(candle['close']), float(candle['volume'])))
    
    CHUNK_SIZE = 200
    futures = []
    MAX_IN_FLIGHT_BATCHES = 20

    for i in range(0, len(data_to_insert), CHUNK_SIZE):
        chunk = data_to_insert[i:i + CHUNK_SIZE]

        batch = BatchStatement(batch_type=BatchType.UNLOGGED, consistency_level=ConsistencyLevel.ONE)
        
        for row in chunk:
            batch.add(prepared, row)

        future = session.execute_async(batch)
        futures.append(future)

        if len(futures) >= MAX_IN_FLIGHT_BATCHES:
            for f in futures:
                f.result()
            futures = []

    for future in futures:
        future.result()

def load_candles_cassandra(crypto_id,  session: Session, limit = 50000):   
    session.row_factory = tuple_factory

    all_candles = []

    current_date = datetime.now(timezone.utc)
    bucket_date = current_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).date()
    
    query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM candles 
        WHERE crypto_id = ? AND bucket_date = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """

    prepared = session.prepare(query)
    prepared.fetch_size = 10000

    points_per_partition = 365 * 24
    
    first_year = 2009
    current_year = datetime.now(timezone.utc).year
    nb_year = current_year - first_year + 1 # 1 + limit // points_per_partition

    futures = []
    limit_per_partition = 366 * 24
    
    for i in range(nb_year):
        target_bucket = (datetime.combine(bucket_date, datetime.min.time()) - relativedelta(years=i)).date()
        future = session.execute_async(prepared, (crypto_id, target_bucket, limit_per_partition))
        futures.append(future)

    all_candles = []
    for future in futures:
        all_candles.extend(future.result())

    return all_candles if limit == -1 else all_candles[:limit]


def save_postgres_candles(crypto_id, candles):
    conn = open_postgres_connection()
    cursor = conn.cursor()

    for candle in candles:
        date = datetime.fromtimestamp(candle['timestamp'] / 1000.0, tz=timezone.utc)
        bucket_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()

        cursor.execute("INSERT INTO public.candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume) VALUES (%s, %s, to_timestamp(%s / 1000.0), %s, %s, %s, %s, %s)", (crypto_id, bucket_date, candle['timestamp'], float(candle['open']), float(candle['high']), float(candle['low']), float(candle['close']), float(candle['volume'])))
    conn.commit()

def load_candles_postgres(crypto_id, limit = 50000):
    conn = open_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, open, high, low, close, volume FROM public.candles WHERE crypto_id = %s ORDER BY timestamp DESC LIMIT %s", (crypto_id, limit))
    return cursor.fetchall()
    