from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from cassandra.cluster import Cluster
import os
import psycopg2
from sqlmodel import Session, create_engine

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

def open_cassandra_connection(keyspace: str = ''):
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    cluster = Cluster(CLUSTER_IPS)
    return cluster.connect(keyspace=keyspace)

def run_cassandra_script(script_name):
    conn = open_cassandra_connection()

    sql = open_script_file(script_name)
    queries = sql.split(';')

    for query in queries:
        query_clean = query.strip() 
        if query_clean:
            conn.execute(query_clean)

def save_cassandra_candles(crypto_id, candles):
    conn = open_cassandra_connection("crypto_bot")

    for candle in candles:
        date = datetime.fromtimestamp(candle['timestamp'] / 1000.0, tz=timezone.utc)
        bucket_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()

        conn.execute("INSERT INTO candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (crypto_id, bucket_date, candle['timestamp'], float(candle['open']), float(candle['high']), float(candle['low']), float(candle['close']), float(candle['volume'])))

def load_candles_cassandra(crypto_id, limit = 50000):   
    conn = open_cassandra_connection("crypto_bot")

    all_candles = []

    current_date = datetime.now(timezone.utc)
    bucket_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    
    query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM candles 
        WHERE crypto_id = ? AND bucket_date = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    prepared = conn.prepare(query)

    while len(all_candles) < limit:
        remaining = limit - len(all_candles)
        rows = conn.execute(prepared, (crypto_id, bucket_date))
        month_candles = list(rows)

        if not month_candles:
            break
            
        all_candles.extend(month_candles)
        
        bucket_date = (datetime.combine(bucket_date, datetime.min.time()) - relativedelta(months=1)).date()

    all_candles = all_candles[:limit]
    clean_candles = [row._asdict() for row in all_candles]

    return clean_candles