import matplotlib.pyplot as plt
import numpy as np
import numpy as np
import pandas as pd

from services.ingestion import build_dict
from services.ingestion import fetch_coin
from src.MachineLearningV1 import MachineLearningV1

def test_ml():

    # Récupération de l'historique
    symbol = 'BTC/USDT'
    limit = 50000
    timeframe = '1h'
    exchange_dict = build_dict()
    candles = fetch_coin(exchange_dict, symbol, timeframe, limit)

    ml = MachineLearningV1(candles)

    print(len(candles))
    ml.clean()
    print(len(ml.candles))

    df = ml.candles
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(df['timestamp'], df['close'])
    fig.savefig('candles_ml_h.png')
    plt.close(fig)

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

    assert ml.score()['train'] > 0.8 and ml.score()['test'] > 0