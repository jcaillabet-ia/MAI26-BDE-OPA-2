import ccxt.pro as ccxtpro
from fastapi import APIRouter
import joblib
import json
from pathlib import Path
import numpy as np

from services.clients import build_dict
from services.ingestion import run_ingestion
from src.MachineLearningV1 import MachineLearningV1

router = APIRouter()

@router.post("/train")
def train(symbol : str):
    # TODO : remplacer par la récupération en base
    limit = 50000
    timeframe = '1h'
    exchange_dict = build_dict()

    run_ingestion(asset='BTC', n_points=50000, timeframe='1h', output_path='test.json')

    with open('test.json', 'r') as f:
        raw_data = json.load(f)
        raw_candles = raw_data['ohlcv']

    ml = MachineLearningV1(raw_candles)

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

    bougie = ohlcv[-1]

    query = np.array([
        bougie[0],
        bougie[1],
        bougie[2],
        bougie[3],
        bougie[5],
    ])
    query = query.reshape(1, -1)

    ml = joblib.load("data/models/" + model_file + ".pkl")
    return ml.predict(query)[0].item()
    