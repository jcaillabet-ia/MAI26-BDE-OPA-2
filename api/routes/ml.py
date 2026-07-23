from cassandra.cluster import Session as CassandraSession
import ccxt
import ccxt.pro as ccxtpro
from fastapi import APIRouter, Depends, status, Body, HTTPException
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

@router.get("/transform/{coin_id}")
def transform(coin_id : str, session: CassandraSession = Depends(get_cassandra)):
    candles = load_candles_cassandra(coin_id, session)

    ml = MachineLearningClassification()

    return ml.transform(candles)

@router.post("/train", status_code=status.HTTP_204_NO_CONTENT)
def train(coin_data: dict = Body(...), session: CassandraSession = Depends(get_cassandra)):
    # raw_candles = load_candles_cassandra(coin_data, session)

    # print(coin_data)

    coin_id = coin_data['coin_id']
    data = coin_data['data']
    target_indice = coin_data['target_indice']

    # print(data)

    ml = MachineLearningClassification()

    # ml.clean()
    # ml.setup()

    #try:
    ml.setup(data, target_indice)
    ml.train()
    # except ValueError as error:
    #     raise HTTPException(status_code=500, detail=str(error))

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
        last_candle = await exchangepro.watch_ohlcv(coin['symbol'], timeframe) #
        last_candle = last_candle[0]
    except Exception as e:
        last_candle = exchange.fetch_ohlcv(
            symbol=coin['symbol'],
            timeframe='1h',
            limit=1,
        )[0]
    finally:
        await exchangepro.close()

    since = last_candle[0] - (10 * (1 * 60 * 60 * 1000) )
    candles = exchange.fetch_ohlcv(
                symbol=coin['symbol'],
                timeframe='1h',
                since=since,
                limit=11,
            )
    candles.append(last_candle)

    ml = MachineLearningClassification()

    transform = ml.transform(candles)

    target_indice = transform['target_indice']
    data = transform['data']
    
    df = pd.DataFrame(data)
    features = df.drop(columns=[target_indice])
    candle = features.values.tolist()[-1]
    print(candle)

    query = np.array([candle[:15]])

    ml = joblib.load(f"/app/data/models/{coin_id}.pkl")

    return ml.predict(query)[0].item()
    