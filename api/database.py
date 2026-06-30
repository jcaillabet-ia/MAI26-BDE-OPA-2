import os
from datetime import datetime
import time
import psycopg2
from cassandra.concurrent import execute_concurrent_with_args

# ==========================================
# Cassandra Management Functions
# ==========================================

def create_keyspace(session, name):    
    create_keyspace_query = f"""
        CREATE KEYSPACE IF NOT EXISTS {name} 
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1}};
    """
    session.execute(create_keyspace_query)

def create_cassandra_schema(session, keyspace_name = "crypto_bot"):    
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.candles (
            crypto_id text,
            bucket_date date,
            timestamp timestamp,
            open decimal,
            high decimal,
            low decimal,
            close decimal,
            volume decimal,
            PRIMARY KEY ((crypto_id, bucket_date), timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC);
    """
    session.execute(create_table_query)

def save_candles_cassandra(session, symbol, candles):    
    query = """
        INSERT INTO candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(query)
    
    start = time.time()
    dt_objet = datetime.fromtimestamp(candles[0][0] / 1000)
    date = dt_objet.date()
    
    # Prepare arguments for concurrent execution
    args_list = [
        (symbol, date, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5])
        for candle in candles
    ]
    
    # Execute 100 statements concurrently
    execute_concurrent_with_args(session, prepared, args_list, concurrency=100)
    
    end = time.time()
    print("Cassandra save : " + str(end - start))
    return date

def load_candles_cassandra(session, symbol, bucket_date, limit):   
    query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM candles 
        WHERE crypto_id = %s AND bucket_date = %s 
        LIMIT %s
    """
    start = time.time()
    rows = session.execute(query, (symbol, bucket_date, limit))
    end = time.time()
    print("Cassandra load : " + str(end - start))

    return rows.all()


# ==========================================
# PostgreSQL Management Functions
# ==========================================

def open_connection():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
    return psycopg2.connect(database_url, connect_timeout=5)

def create_postgres_schema(conn, schema_name):
    query = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    with conn.cursor() as cursor:
        cursor.execute(query)
    conn.commit()

#def import_postgres_schema(conn)
    # conn = db.open_connection()
    # cursor = conn.cursor()

    # schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    # with open(schema_path, "r") as schema_file:
    #     schema_sql = schema_file.read()

    # cursor.execute(schema_sql)
    # conn.commit()

def create_postgres_table(conn, schema_name = "crypto_bot"):
    query = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.candles (
            crypto_id text,
            bucket_date date,
            timestamp timestamp,
            open decimal,
            high decimal,
            low decimal,
            close decimal,
            volume decimal,
            PRIMARY KEY (crypto_id, bucket_date, timestamp)
        );
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
    conn.commit()

def save_candles_postgres(conn, symbol, candles, schema_name = "crypto_bot"):    
    query = f"""
        INSERT INTO {schema_name}.candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (crypto_id, bucket_date, timestamp) DO NOTHING;
    """
    start = time.time()
    dt_objet = datetime.fromtimestamp(candles[0][0] / 1000.0)
    date = dt_objet.date()
    
    with conn.cursor() as cursor:
        for candle in candles:
            candle_dt = datetime.fromtimestamp(candle[0] / 1000.0)
            cursor.execute(query, (
                symbol,
                date,
                candle_dt,
                candle[1],
                candle[2],
                candle[3],
                candle[4],
                candle[5]
            ))
    conn.commit()
    end = time.time()
    print("Postgres save : " + str(end - start))
    return date

def load_candles_postgres(conn, symbol, bucket_date, limit, schema_name = "crypto_bot"):   
    query = f"""
        SELECT timestamp, open, high, low, close, volume 
        FROM {schema_name}.candles 
        WHERE crypto_id = %s AND bucket_date = %s 
        ORDER BY timestamp DESC
        LIMIT %s
    """
    start = time.time()
    with conn.cursor() as cursor:
        cursor.execute(query, (symbol, bucket_date, limit))
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    end = time.time()
    print("Postgres load : " + str(end - start))

    return rows
