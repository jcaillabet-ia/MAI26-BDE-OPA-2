import ccxt
from datetime import datetime
import pandas as pd

from cassandra.cluster import Cluster

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

import time

def main():
    print("start")

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
        timeframe = '1m'  # Options: '1m', '5m', '1h', '1d', etc.
        limit = 1000         # Nombre de bougies à récupérer

        # Récupération de l'historique
        start = time.time()
        candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        end = time.time()
        #print("Temps de récolte : " + str(end - start))
        #print(f"Nombre de données récoltées : {len(candles)}")

        #print(f"--- Historique des {limit} dernières bougies ({timeframe}) ---")
        query = """
            INSERT INTO candles (crypto_id, bucket_date, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        start = time.time()
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
        end = time.time()
        #print("Temps d'insertion : " + str(end - start))

        start = time.time()
        query = """
            SELECT timestamp, open, high, low, close, volume 
            FROM candles 
            WHERE crypto_id = %s AND bucket_date = %s 
            LIMIT %s
        """
        # On exécute la requête ciblée sur une partition précise
        rows = session.execute(query, (symbol, date, limit))
        end = time.time()
        #print("Temps de récupération : " + str(end - start))

        #print(f"\n--- Dernières entrées dans Cassandra pour {symbol} ({date}) ---")
        #for row in rows:
        #    print(f"Time: {row.timestamp} | Open: {row.open:.2f} | Close: {row.close:.2f} | Vol: {row.volume:.2f}")
      
        all_rows = rows.all()
        #print(f"Nombre de données récupérées : {len(all_rows)}")
        
        df = pd.DataFrame(all_rows)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        X = df.drop('close', axis = 1)
        X['timestamp'] = pd.to_datetime(X['timestamp']).astype(int)

        Y = df['close']

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2, random_state=42)

        dt_reg = DecisionTreeRegressor(random_state=42)
        dt_reg.fit(X_train, y_train)

        y_pred_test = dt_reg.predict(X_test)

        print(y_test - y_pred_test)

        print("score train : " , dt_reg.score(X_train, y_train))
        print("score test : ", dt_reg.score(X_test,y_test))
        
    finally:
        # On ferme proprement les connexions
        cluster.shutdown()
        

if __name__ == "__main__":
    main()
