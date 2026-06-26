import os
from fastapi import APIRouter, Request

from services.coin import list_coins, enable_coin

router = APIRouter()

@router.get("/")
def list(request: Request):
    return list_coins()
    return templates.TemplateResponse(
        request=request, 
        name="index.html",
        context={"coins": coins}
    )

@router.patch("/{id}/enable")
def enable(id: str):
    coin = enable_coin(id)
    return coin
    