from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSkipException
import json

import httpx
from typing import List

@task
def pull_catalog() -> List[str]:
    coins = httpx.get(f"http://api:8000/coin/").json()
    enabled_coins = list(filter(lambda coin: coin['enabled'], coins))
    ids = list(map(lambda coin: coin['id'], enabled_coins))
    return ids

@task
def process_single_coin(coin_id: str):
    print(f"COIN: {coin_id}")
    return coin_id

@task
def get_interval(coin_id: str):
    interval = httpx.get(f"http://api:8000/candle/{coin_id}/interval").json()
    print(f"LAST {coin_id}:")
    print(interval)
    return {"coin_id":coin_id, "interval":interval}

@task
def past_ingestion(coin_data: dict):
    coin_id = coin_data["coin_id"]
    interval = coin_data["interval"]

    with httpx.Client(timeout=None) as client:
        response = client.post("http://api:8000/ingestion/run", 
            json={
                "coin_id": coin_id,
                "timeframe": "1h",
                "n_points": 1000
            }
        )
        response.raise_for_status()
        json = response.json()
        print(json)
        return json['output_path']

@task
def present_ingestion(coin_data: dict):
    coin_id = coin_data["coin_id"]
    interval = coin_data["interval"]

    if interval["last"] is None:
        raise AirflowSkipException(f"Coin {coin_data['coin_id']} n'est pas concerné.")

@task
def read_file(output_path: str):
    with open(output_path, 'r') as f:
        data = json.load(f)

    coin_id = output_path.split('/')[-1].split('.')[0]
    candles = data['ohlcv']

    return {
        "coin_id": coin_id,
        "candles": candles
    }

# @task
# def transform_data(data):
#     coin_id = data['coin_id']
#     candles = data['candles']
    
#     df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)

#     raw_candles = df.to_dict('records')

#     return {
#         "coin_id": coin_id,
#         "candles": raw_candles
#     }

@task
def load_data(coin_data: dict):
    coin_id = coin_data['coin_id']
    candles = coin_data['candles']

    httpx.post(f"http://api:8000/candle/{coin_id}/save", 
        json={
            "id": coin_id,
            "candles": candles
        }
    )

    return coin_id

@task
def train_model(coin_id: str):
    try:
        r = httpx.post("http://api:8000/ml/train", 
            json={
                "coin_id": coin_id
            },
            timeout=0.5
        )
    except httpx.TimeoutException:
        pass

@task_group(group_id="main_pipeline")
def main_pipeline(coin_id_list: List[str]):
    t2 = process_single_coin.expand(coin_id=coin_id_list)

    t3 = get_interval.expand(coin_id=t2)

    t4 = past_ingestion.expand(coin_data=t3)
    present_ingestion.expand(coin_data=t3)

    t6 = read_file.expand(output_path=t4)
    
    t7 = load_data.expand(coin_data=t6)
    
    train_model.expand(coin_id=t7)