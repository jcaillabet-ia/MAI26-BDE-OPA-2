from fastapi import APIRouter, status

from services.coin import list_coins, enable_coin, disable_coin

router = APIRouter()

@router.get("/")
def list():
    return list_coins()

@router.patch("/{id}/enable", status_code=status.HTTP_204_NO_CONTENT)
def enable(id: str):
    coin = enable_coin(id)
    return coin

@router.patch("/{id}/disable", status_code=status.HTTP_204_NO_CONTENT)
def enable(id: str):
    coin = disable_coin(id)
    return coin
    