import os
from fastapi import APIRouter, Request

from services.ingestion import build_dict

router = APIRouter()

@router.get("/register")
def register():
    return build_dict()
    # result = []
    # coins = list_coins()
    # for coin in coins:
    #     item = {'id': coin['symbol']}
    #     if 'ticker' in coin:
    #         item['ticker'] = coin['ticker']
    #     result.append(item)
    # return result