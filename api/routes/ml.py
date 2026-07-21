from cassandra.cluster import Session as CassandraSession
import ccxt
import ccxt.pro as ccxtpro
from fastapi import APIRouter, Depends, status, Body
import joblib
from pathlib import Path
import numpy as np
from sqlmodel import Session, select
import pandas as pd

from dependencies import get_cassandra
from models.Coin import Coin
from services.coin import list_coins
from services.database import load_candles_cassandra
from services.database import engine
from services.ingestion import run_ingestion
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

    chemin_fichier = Path("/app/data/models/" + coin_id + ".pkl")

    with Session(engine) as session:
        statement = select(Coin).where(Coin.id == coin_id)
        coin = session.exec(statement).first()

        if score >= coin.score or coin.score == 0:
            
            chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

            coin.score = score
            coin.save(session)
            
    
    joblib.dump(ml.model, chemin_fichier)

@router.post("/predict")
async def predict(coin_id: str = Body(..., embed=True)):
    timeframe = '1h'

    coins = list_coins()
    coin = list(filter(lambda x: x['id'] == coin_id, coins))[0]

    exchange_name = coin['exchange']
    exchange = getattr(ccxt, exchange_name)()
    exchangepro = getattr(ccxtpro, exchange_name)()

    last_candle = []
    try:
        last_candle = await exchangepro.watch_ohlcv(coin['symbol'], timeframe)
        last_candle = last_candle[0]
    finally:
        await exchangepro.close()

    since = last_candle[0] - (10 * (1 * 60 * 60 * 1000) )
    candles = exchange.fetch_ohlcv(
                symbol=coin['symbol'],
                timeframe='1h',
                since=since,
                limit=10,
            )
    candles.append(last_candle)

    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    candle = df.iloc[-1]
    for i in range(1, 9):
        df['close_m-{}'.format(i)] = df['close'].shift(i)
    df = df.dropna()
    candle = df.iloc[-1].tolist()

    query = np.array([
        candle[0],
        candle[1],
        candle[2],
        candle[3],
        candle[4],
        candle[5],
        candle[6],
        candle[7],
        candle[8],
        candle[9],
        candle[10],
        candle[11],
        candle[12],
        candle[13],
    ])
    query = query.reshape(1, -1)

    ml = joblib.load(f"/app/data/models/{coin_id}.pkl")
    return ml.predict(query)[0].item()
    