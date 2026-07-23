from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import datetime
import httpx
from typing import List

from common.tasks import main_pipeline, pull_catalog

@dag(
    dag_id='cryptobot_ingestion',
    tags=['crypto_bot'],
    schedule = "@monthly",
    start_date=datetime(2026, 7, 1),
    catchup=False
)

def ingestion_dag():
    t1 = pull_catalog()

    t2 = main_pipeline(coin_id_list=t1)

ingestion_dag = ingestion_dag()