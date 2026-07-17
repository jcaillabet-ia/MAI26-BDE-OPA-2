from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

@task
def task1():
    pass

@dag(
    dag_id='cryptobot_ingestion',
    tags=['crypto_bot'],
    schedule_interval = "* * * * *",
    start_date=days_ago(0),
    catchup=False
)
def ingestion_dag():
    t1 = task1()

ingestion_dag = ingestion_dag()