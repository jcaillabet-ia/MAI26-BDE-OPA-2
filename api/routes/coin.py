from fastapi import APIRouter, status
import httpx

from services.coin import list_coins, enable_coin, disable_coin, get_coin

router = APIRouter()

@router.get("/")
def list():
    return list_coins()

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
    