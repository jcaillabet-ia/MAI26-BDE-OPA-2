from pandas.core.interchange import dataframe
from sklearn.ensemble import RandomForestRegressor
import ccxt
import pandas as pd
import numpy as np

from cassandra.cluster import Cluster

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

import time

def main():
    exchange = ccxt.binance()

    # Configuration
    symbol = 'BTC/USDT'
    timeframe = '1m'
    limit = 1000

    # Récupération de l'historique
    start = time.time()
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    end = time.time()

    # print("Temps de récolte : " + str(end - start))
    # print(f"Nombre de données récoltées : {len(candles)}")

    #since_timestamp = candles[0][0]
    #trades = exchange.fetch_trades(symbol, since=since_timestamp)
    #pprint.pprint(trades[:5])

    df = pd.DataFrame(candles, columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    df.sort_values('timestamp', inplace=True)

    # df.set_index('timestamp', inplace=True)

    df_clean = pd.DataFrame()

    #df.index.head()
    data_times = pd.to_datetime(df.timestamp, unit='ms')

    df_clean['minute_of_day'] = data_times.dt.hour * 60 + data_times.dt.minute
    df_clean['day_of_week'] = data_times.dt.dayofweek
    df_clean['time_sin'] = np.sin(2 * np.pi * df_clean['minute_of_day'] / 1440.0)
    df_clean['time_cos'] = np.cos(2 * np.pi * df_clean['minute_of_day'] / 1440.0)
    df_clean['day_sin'] = np.sin(2 * np.pi * df_clean['day_of_week'] / 7.0)
    df_clean['day_cos'] = np.cos(2 * np.pi * df_clean['day_of_week'] / 7.0)

    df_clean['feat_close'] = df['close'].pct_change()
    df_clean['feat_open'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    df_clean['feat_high'] = (df['high'] - df['open']) / df['open']
    df_clean['feat_low'] = (df['open'] - df['low']) / df['open']
    df_clean['feat_volume'] = df['volume']
    df_clean['target'] = df_clean['feat_close'].shift(-1)

    for i in range(1, 4):
        df_clean[f'feat_close_lag_{i}'] = df_clean['feat_close'].shift(i)
        df_clean[f'feat_volume_lag_{i}'] = df_clean['feat_volume'].shift(i)

    df_clean.dropna(inplace=True)

    split_index = int(len(df) * 0.8)

    X = df_clean[['time_sin', 'time_cos', 'day_sin', 'day_cos', 'feat_open', 'feat_close', 'feat_high', 'feat_low', 'feat_volume', 'feat_close_lag_1', 'feat_volume_lag_1', 'feat_close_lag_2', 'feat_volume_lag_2', 'feat_close_lag_3', 'feat_volume_lag_3']]
    # Notre cible : le close de la bougie SUIVANTE (t+1)
    # On crée la cible en décalant la colonne 'close' brute vers le passé
    y = df_clean['target']

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    #print(f"--- Historique des {limit} dernières bougies ({timeframe}) ---")
    # df = pd.DataFrame(all_rows)
    # for col in ['open', 'high', 'low', 'close', 'volume']:
    #     df[col] = df[col].astype(float)
    
    # X = df.drop('close', axis = 1)
    # X['timestamp'] = pd.to_datetime(X['timestamp']).astype(int)

    # Y = df['close']

    # X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    y_pred_test = model.predict(X_test)

    print("score train : " , model.score(X_train, y_train))
    print("score test : ", model.score(X_test,y_test))

if __name__ == "__main__":
    main()
