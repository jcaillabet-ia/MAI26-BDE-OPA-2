from cassandra.cluster import Session as CassandraSession
import ccxt.pro as ccxtpro
from fastapi import APIRouter, Depends, status, Body
import joblib
from pathlib import Path
import numpy as np
from sqlmodel import Session, select

from dependencies import get_cassandra
from models.Coin import Coin
from services.clients import build_dict
from services.database import load_candles_cassandra
from services.database import engine
from src.MachineLearningClassification import MachineLearningClassification

router = APIRouter()

@router.post("/train", status_code=status.HTTP_204_NO_CONTENT)
def train(coin_id : str = Body(..., embed=True), session: CassandraSession = Depends(get_cassandra)):
    raw_candles = load_candles_cassandra(coin_id, session)

    ml = MachineLearningClassification(raw_candles)

    ml.clean()
    ml.setup()
    ml.train()

    ml.predict(ml.X_test)
    score = ml.score()

    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()

        if score >= coin.score or coin.score == 0:
            chemin_fichier = Path("/app/data/models/" + coin_id + ".pkl")
            chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

            coin.score = score
            coin.save(session)
            
    
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
    