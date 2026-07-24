from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import datetime
import httpx
from typing import List

from common.tasks import pull_catalog

@task
def request_candle(coin_id: str):
    candle = httpx.get(f"http://api:8000/ingestion/stream/{coin_id}").json()
    return {"coin_id":coin_id, "candle":candle}

@task
def load_data(coin_data: dict):
    coin_id = coin_data['coin_id']
    candle = coin_data['candle']

    httpx.post(
        f"http://api:8000/candle/{coin_id}/save", 
        json={
            "id": coin_id,
            "candles": [candle]
        }
    )

    pass

@dag(
    dag_id='cryptobot_streaming',
    tags=['crypto_bot'],
    schedule = "@hourly",
    start_date=datetime(2026, 7, 21),
    catchup=False
)
def ingestion_dag():
    t1 = pull_catalog()

    t2 = request_candle.expand(coin_id=t1)

    t3 = load_data.expand(coin_data=t2)

ingestion_dag = ingestion_dag()