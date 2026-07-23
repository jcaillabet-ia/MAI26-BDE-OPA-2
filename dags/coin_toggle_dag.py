from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import datetime
import httpx
import os

from common.tasks import main_pipeline

@task.branch
def action_branching(**context):
    params = context['dag_run'].conf
    command = params.get('command')
    
    if command == "enable":
        return "enable_coin"
    elif command == "disable":
        return "disable_coin"

@task
def enable_coin(**context):
    params = context['dag_run'].conf
    coin_id = params.get('coin_id')

    return [coin_id]

@task
def disable_coin(**context):
    params = context['dag_run'].conf
    coin_id = params.get('coin_id')

    return coin_id

@task
def remove_candles(coin_id: str):
    httpx.post(f"http://api:8000/candle/{coin_id}/delete")

    return coin_id

@task
def clear_files(coin_id: str):
    output_path = f"/app/data/candles/{coin_id}.json"
    print(output_path)
    if os.path.exists(output_path):
        print("delete candles")
        os.remove(output_path)

    output_path = f"/app/data/models/{coin_id}.pkl"
    print(output_path)
    if os.path.exists(output_path):
        print("delete model")
        os.remove(output_path)

@dag(
    dag_id='cryptobot_coin_toggle',
    tags=['crypto_bot'],
    schedule_interval = None,
    start_date=datetime(2026, 1, 1),
    catchup=False
)

def coin_toggle_dag():
    t1 = action_branching()

    t2 = enable_coin()
    t3 = disable_coin()

    t1 >> [t2, t3]

    t4 = main_pipeline(t2)

    t5 = remove_candles(t3)
    t6 = clear_files(t5)

coin_toggle_dag = coin_toggle_dag()