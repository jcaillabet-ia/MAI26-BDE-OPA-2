import ccxt
from datetime import datetime

from cassandra.cluster import Cluster

def main():
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    
    cluster = Cluster(CLUSTER_IPS)
    
    try:
        session = cluster.connect()
        session.set_keyspace('crypto_bot')
        
        create_keyspace_query = """
            CREATE KEYSPACE IF NOT EXISTS crypto_bot 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
        """
        create_table_query = """
            CREATE TABLE IF NOT EXISTS crypto_bot.candles (
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

        session.execute(create_keyspace_query)
        session.execute(create_table_query)

        exchange = ccxt.binance()

        # Configuration
        symbol = 'BTC/USDT'
        timeframe = '1h'  # Options: '1m', '5m', '1h', '1d', etc.
        limit = 5         # Nombre de bougies à récupérer

        # Récupération de l'historique
        candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        print(candles)
        #print(f"--- Historique des {limit} dernières bougies ({timeframe}) ---")
        query = """
            INSERT INTO candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        for candle in candles:
            dt_objet = datetime.fromtimestamp(candle[0] / 1000)
            timestamp_cassandra = dt_objet  # Contient la date ET l'heure
            date = dt_objet.date()

            # Cassandra requiert des types précis, on convertit les floats en chaînes ou types compatibles
            session.execute(query, (
                symbol,
                date,
                candle[0],
                candle[1],
                candle[2],
                candle[3],
                candle[4],
                candle[5]
            ))

        query = """
            SELECT timestamp, open, close, volume 
            FROM candles 
            WHERE crypto_id = %s AND bucket_date = %s 
            LIMIT %s
        """
        # On exécute la requête ciblée sur une partition précise
        rows = session.execute(query, (symbol, date, limit))
    
        print(f"\n--- Dernières entrées dans Cassandra pour {symbol} ({date}) ---")
        for row in rows:
            print(f"Time: {row.timestamp} | Open: {row.open:.2f} | Close: {row.close:.2f} | Vol: {row.volume:.2f}")
      
    finally:
        # On ferme proprement les connexions
        cluster.shutdown()
        

if __name__ == "__main__":
    main()
