from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import datetime
import httpx

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

    coin = httpx.get(f"http://api:8000/coin/{coin_id}").json()
    symbol = coin['symbol'].split('/')[0]
    print(symbol)
    try:
        r = httpx.post("http://api:8000/ingestion/run", 
            json={
                "asset": symbol,
                "timeframe": "1h",
                "n_points": 50000
            },
            timeout=0.5
        )
    except httpx.TimeoutException:
        pass
        

@task
def disable_coin():
    pass

@dag(
    dag_id='cryptobot_coin_toggle',
    tags=['crypto_bot'],
    schedule_interval = None,
    start_date=datetime(2026, 1, 1),
    catchup=False
)
def coin_toggle_dag():
    t2 = enable_coin()
    t3 = disable_coin()

    action_branching() >> [t2, t3]

coin_toggle_dag = coin_toggle_dag()