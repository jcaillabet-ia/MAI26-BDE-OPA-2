from fastapi import APIRouter, status, HTTPException
import httpx
from psycopg2 import errors
from sqlalchemy.exc import ProgrammingError

from services.coin import list_coins, enable_coin, disable_coin, get_coin

router = APIRouter()

@router.get("/")
def list():
    """
    Liste les cryptomonnaies qu'il est possible de gérer
    """

    try:
        list = list_coins()
        return list
    except ProgrammingError as e:
        raise HTTPException(status_code=500, detail="La base de données PostgreSQL n'a pas été initialisée.")

@router.get("/{id}")
def item(id: str):
    coin = get_coin(id)
    return coin

@router.patch("/{id}/enable", status_code=status.HTTP_204_NO_CONTENT)
def enable(id: str):
    enable_coin(id)
    httpx.post("http://airflow-webserver:8080/api/v1/dags/cryptobot_coin_toggle/dagRuns", 
        json={"conf":{
                "command": "enable", 
                "coin_id": id}
            },
        auth=("airflow", "airflow"))

@router.patch("/{id}/disable", status_code=status.HTTP_204_NO_CONTENT)
def disable(id: str):
    disable_coin(id)
    httpx.post("http://airflow-webserver:8080/api/v1/dags/cryptobot_coin_toggle/dagRuns", 
        json={"conf":{
                "command": "disable", 
                "coin_id": id}
            },
        auth=("airflow", "airflow"))