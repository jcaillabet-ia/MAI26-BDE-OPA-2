import ccxt.pro as ccxtpro
from fastapi import APIRouter
import joblib
from pathlib import Path
import numpy as np

from services.ingestion import build_dict
from services.ingestion import fetch_coin
from src.MachineLearningV1 import MachineLearningV1

router = APIRouter()

@router.post("/train")
def train(symbol : str):

    # TODO : remplacer par la récupération en base
    limit = 50000
    timeframe = '1h'
    exchange_dict = build_dict()
    candles = fetch_coin(exchange_dict, symbol, timeframe, limit)

    ml = MachineLearningV1(candles)

    ml.clean()
    ml.setup()
    ml.train()

    indice = 1
    chemin_fichier = Path("data/models/" + symbol.replace("/", "-") + "-" + str(indice) + ".pkl")
    chemin_fichier.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(ml.model, chemin_fichier)

@router.post("/predict")
async def predict(model_file, symbol: str):
    timeframe = '1h'

    register = build_dict()

    exchange_name = list(filter(lambda x: x['symbol'] == symbol, register))[0]['exchange']
    exchange = getattr(ccxtpro, exchange_name)()

    ohlcv = await exchange.watch_ohlcv(symbol, timeframe)

    # On récupère la dernière bougie du tableau
    bougie = ohlcv[-1]

    query = np.array([
        bougie[0],
        bougie[1],
        bougie[2],
        bougie[3],
        bougie[5],
    ])
    query = query.reshape(1, -1)

    print(query)

    # timestamp, open_p, high, low, close, volume = derniere_bougie
    # date_lisible = exchange.iso8601(timestamp)

    ml = joblib.load("data/models/" + model_file + ".pkl")
    return ml.predict(query)[0].item()
    