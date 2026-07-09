from fastapi import APIRouter, HTTPException

from services import ingestion as ingestion_service


router = APIRouter()


@router.post("/run")
def run_ingestion(
    asset: str = "BTC",
    timeframe: str = "1h",
    n_points: int = 100,
    limit_per_request: int = 1000,
):
    """
    Lance une ingestion OHLCV via le service d'ingestion.

    Cette route ne contient pas la logique CCXT.
    Elle délègue au dossier services.
    """
    try:
        return ingestion_service.run_ingestion(
            asset=asset,
            timeframe=timeframe,
            n_points=n_points,
            limit_per_request=limit_per_request,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
