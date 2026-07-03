import pandas as pd

from cassandra.cluster import Cluster

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from coin import fetch_coin
from database import create_keyspace, create_cassandra_schema, save_candles_cassandra, load_candles_cassandra
from database import open_connection, create_postgres_schema, create_postgres_table, save_candles_postgres, load_candles_postgres

from time import *

from coingecko import build_dict

import matplotlib.pyplot as plt
import numpy as np

def main():
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    cluster = Cluster(CLUSTER_IPS)
    session = cluster.connect()

    # Configuration
    base = 'BTC'
    quote = 'USDT'
    symbol = base + '/' + quote
    limit = 50000

    try:
        # Keyspace
        #create_keyspace(session, "crypto_bot")
        #session.set_keyspace('crypto_bot')

        # Table
        #create_cassandra_schema(session, "crypto_bot")

        # Appel ccxt
        # exchange_dict = build_dict()
        # candles = fetch_coin(exchange_dict, symbol, limit)

        # fig, ax = plt.subplots( nrows=1, ncols=1 )
        # ax.plot(list(map(lambda x: x[0], candles)), list(map(lambda x: x[4], candles)))
        # fig.savefig('candles_ccxt.png')
        # plt.close(fig) 

        # bucket_date = save_candles_cassandra(session, symbol, candles)

        #print(bucket_date)
        #return
        
        #bucket_date = time.now()
        rows = load_candles_cassandra(session, symbol, '2026-05-27', limit)

        fig, ax = plt.subplots( nrows=1, ncols=1 )
        ax.plot(list(map(lambda x: x.timestamp, rows)), list(map(lambda x: x.close, rows)))
        fig.savefig('candles_cassandra.png')
        plt.close(fig) 

        # test postgres
        # conn = open_connection()
        # create_postgres_schema(conn, "crypto_bot")
        # create_postgres_table(conn, "crypto_bot")
        # save_candles_postgres(conn, symbol, candles)
        # load_candles_postgres(conn, symbol, bucket_date, limit)
        # conn.close()


        df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        print("Taille: ", len(df))
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df.sort_values(by='timestamp', ascending=True, inplace=True)

        X = df.drop('close', axis = 1)
        X['timestamp'] = pd.to_datetime(X['timestamp']).astype(int)

        Y = df['close']

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.75, random_state=42, shuffle=False)

        dt_reg = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42) 
        dt_reg.fit(X_train, y_train)

        y_pred_test = dt_reg.predict(X_test)

        print(y_test - y_pred_test)

        print("score train : " , dt_reg.score(X_train, y_train))
        print("score test : ", dt_reg.score(X_test, y_test))

        X_plot = pd.concat([X_train, X_test])
        y_plot = np.concatenate((y_train, y_test))
        fig, ax = plt.subplots( nrows=1, ncols=1 )
        ax.plot(X_plot['timestamp'], y_plot)
        fig.savefig('candles_ml_train.png')
        plt.close(fig) 

        X_plot = pd.concat([X_train, X_test])
        y_plot = np.concatenate((y_train, y_pred_test))
        fig, ax = plt.subplots( nrows=1, ncols=1 )
        # ax.plot(X_plot['timestamp'], y_plot)

        plt.plot(X_train['timestamp'], y_train, color='royalblue', label='Données d\'entraînement')
        plt.plot(X_test['timestamp'], y_pred_test, color='crimson', label='Prédiction ML')

        fig.savefig('candles_ml_predict.png')
        plt.close(fig) 
    # except Exception as e:
    #     print(e)
    finally:
        print()
        ##cluster.shutdown()
        
if __name__ == "__main__":
    main()
