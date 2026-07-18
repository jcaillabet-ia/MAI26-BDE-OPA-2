from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import datetime
import json
import pandas as pd
import httpx

@task
def read_files(**context):
    params = context['dag_run'].conf
    file = params.get('file')
    # print(file)

    with open(file, 'r') as f:
        data = json.load(f)

    task_instance = context['task_instance']
    task_instance.xcom_push(
        key="data",
        value=data
    )

@task
def transform_data(**context):
    task_instance = context['task_instance']
    data = task_instance.xcom_pull(key="data")
    
    df = pd.DataFrame(data['ohlcv'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
    
    raw_candles = df.to_dict('records')

    task_instance.xcom_push(
        key="data",
        value=raw_candles
    )


@task
def load_data(**context):
    task_instance = context['task_instance']
    data = task_instance.xcom_pull(key="data")
    
    try:
        r = httpx.post("http://api:8000/candles/load", 
            json={
                "candles": data
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
    t2 = transform_data()
    t3 = load_data()
    
    t1 >> t2 >> t3

load_candles_dag = load_candles_dag()