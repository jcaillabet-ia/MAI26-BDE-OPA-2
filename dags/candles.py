from airflow.decorators import dag, task
from datetime import datetime
import json
import pandas as pd
import httpx

@task
def read_files(**context):
    params = context['dag_run'].conf
    path = params.get('path')

    with open(path, 'r') as f:
        data = json.load(f)

    coin_id = path.split('/')[-1].split('.')[0]
    candles = data['ohlcv']

    return {
        "coin_id": coin_id,
        "candles": candles
    }

@task
def transform_data(data):
    coin_id = data['coin_id']
    candles = data['candles']
    
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)

    raw_candles = df.to_dict('records')

    return {
        "coin_id": coin_id,
        "candles": raw_candles
    }

@task
def load_data(data):
    coin_id = data['coin_id']
    candles = data['candles']

    r = httpx.post(f"http://api:8000/candle/{coin_id}/save", 
        json={
            "id": coin_id,
            "candles": candles
        }
    )

    return coin_id

@task
def train_model(coin_id):
    try:
        r = httpx.post("http://api:8000/ml/train", 
            json={
                "coin_id": coin_id
            },
            timeout=0.5
        )
    except httpx.TimeoutException:
        pass

@dag(
    dag_id='cryptobot_load_candles',
    tags=['crypto_bot'],
    schedule_interval = None,
    start_date=datetime(2026, 1, 1),
    catchup=False
)
def load_candles_dag():
    t1 = read_files()
    t2 = transform_data(t1)
    t3 = load_data(t2)
    t4 = train_model(t3)

load_candles_dag = load_candles_dag()