from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


def print_hello():
    print("Hello from Airflow! This DAG runs every second.")
    return "Text displayed successfully"


# Définition du DAG qui s'exécute toutes les secondes
dag = DAG(
    'hello_every_second',
    schedule=timedelta(seconds=1),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        'owner': 'airflow',
        'retries': 1,
    }
)

# Tâche qui appelle la fonction Python
task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)
