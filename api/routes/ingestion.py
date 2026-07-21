
from fastapi import APIRouter, HTTPException, Body
import httpx
from pydantic import BaseModel

from services import ingestion as ingestion_service
from services.coin import get_coin

router = APIRouter()

class IngestionPayload(BaseModel):
    coin_id: str = "bitcoin"
    timeframe: str = "1h"
    n_points: int = 100
    limit_per_request: int = 1000

@router.post("/run")
def run_ingestion(payload: IngestionPayload):
    """
    Lance une ingestion OHLCV via le service d'ingestion.

    Cette route ne contient pas la logique CCXT.
    Elle délègue au dossier services.
    """

    coin = get_coin(payload.coin_id)
    asset = coin['symbol'].split('/')[0]

    try:
        output_path=f"/app/data/candles/{payload.coin_id}.json"
        result = ingestion_service.run_ingestion(
            asset=asset,
            timeframe=payload.timeframe,
            n_points=payload.n_points,
            limit_per_request=payload.limit_per_request,
            output_path=output_path
        )

        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/stream/{coin_id}")
async def stream_candle(coin_id: str):
    """
    Retourne la bougie la plus recente disponible chez ccxt ( en passant par les websockets )
    """

    return await ingestion_service.query_candle(coin_id)
