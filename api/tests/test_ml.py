import json
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
import pandas as pd

from cassandra.cluster import Cluster

from sklearn.metrics import classification_report

from services.database import save_cassandra_candles, load_candles_cassandra
from services.ingestion import build_dict, run_ingestion
from src.MachineLearningClassification import MachineLearningClassification

def test_ml():
    CLUSTER_IPS = ['cassandra.mai26-bde-opa-2.orb.local'] 
    keyspace = "crypto_bot"
    cluster = Cluster(CLUSTER_IPS)
    session = cluster.connect(keyspace=keyspace)


    # Récupération de l'historique
    symbol = 'BTC/USDT'
    limit = 50000
    timeframe = '1h'
    exchange_dict = build_dict()
    
    # candles = fetch_coin(exchange_dict, symbol, timeframe, limit)
    
    # run_ingestion(asset='BTC', n_points=50000, timeframe='1h', output_path='test.json')

    # with open('test.json', 'r') as f:
    #     raw_data = json.load(f)
    #     raw_candles = raw_data['ohlcv']

    # save_cassandra_candles('bitcoin', raw_candles)

    candles = load_candles_cassandra('bitcoin', session=session)
    
    # print(len(candles))

    print("Load ok")

    ml = MachineLearningClassification(candles)

    # print(len(candles))
    ml.clean()
    #print(len(ml.candles))

    # print(ml.candles.head())
    # return

    df = ml.candles
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(df['timestamp'], df['close'])
    fig.savefig('candles_ml_h.png')
    plt.close(fig)

    # return

    ml.clean()
    ml.setup()
    ml.train()

    X_plot = pd.concat([ml.X_train, ml.X_test])
    y_plot = np.concatenate((ml.y_train, ml.y_test))
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(X_plot['timestamp'], y_plot)
    fig.savefig('candles_ml_train.png')
    plt.close(fig)

    y_pred_test = ml.predict(ml.X_test)

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    plt.plot(ml.X_train['timestamp'], ml.y_train, color='royalblue', label='Données d\'entraînement')
    plt.plot(ml.X_test['timestamp'], y_pred_test, color='crimson', label='Prédiction ML')
    fig.savefig('candles_ml_predict.png')
    plt.close(fig)

    print(ml.score())

    assert ml.score() > 0