import os
from datetime import datetime
import time
import psycopg2
from cassandra.concurrent import execute_concurrent_with_args

# ==========================================
# Cassandra Management Functions
# ==========================================

def save_candles_cassandra(session, symbol, candles):    
    query = """
        INSERT INTO crypto_bot.candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume)
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
        FROM crypto_bot.candles 
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
