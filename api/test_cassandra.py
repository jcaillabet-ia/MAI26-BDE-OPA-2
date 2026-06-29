import ccxt
from datetime import datetime
import pandas as pd

from cassandra.cluster import Cluster

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

from coin import fetch_coin
from database import create_keyspace, create_cassandra_schema, save_candles_cassandra, load_candles_cassandra
from database import open_connection, create_postgres_schema, create_postgres_table, save_candles_postgres, load_candles_postgres

def main():
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    cluster = Cluster(CLUSTER_IPS)
    session = cluster.connect()

    try:
        # Keyspace
        create_keyspace(session, "crypto_bot")
        session.set_keyspace('crypto_bot')

        # Table
        create_cassandra_schema(session, "crypto_bot")

        exchange = ccxt.binance()

        # Configuration
        symbol = 'BTC/USDT'
        limit = 40000
        candles = fetch_coin(symbol, limit)

        bucket_date = save_candles_cassandra(session, symbol, candles)
        rows = load_candles_cassandra(session, symbol, bucket_date, limit)

        # test postgres
        conn = open_connection()
        create_postgres_schema(conn, "crypto_bot")
        create_postgres_table(conn, "crypto_bot")
        save_candles_postgres(conn, symbol, candles)
        load_candles_postgres(conn, symbol, bucket_date, limit)
        conn.close()

        df = pd.DataFrame(rows)
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
    # except Exception as e:
    #     print(e)
    finally:
        cluster.shutdown()
        
if __name__ == "__main__":
    main()
