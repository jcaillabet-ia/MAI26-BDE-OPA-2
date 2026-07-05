import os
from fastapi import APIRouter, Request

from services.coin import list_coins, enable_coin, disable_coin

router = APIRouter()

@router.get("/")
def list():
    return list_coins()
    

@router.patch("/{id}/enable")
def enable(id: str):
    coin = enable_coin(id)
    return coin

@router.patch("/{id}/disable")
def enable(id: str):
    coin = disable_coin(id)
    return coin
    