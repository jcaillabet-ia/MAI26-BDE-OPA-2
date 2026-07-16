from cassandra.cluster import Session
from fastapi import APIRouter, Depends

from dependencies import get_cassandra
from services.database import load_candles_cassandra, save_cassandra_candles

router = APIRouter()

@router.get("/{id}/list")
def list(id: str, session: Session = Depends(get_cassandra)):
    return load_candles_cassandra(id, session)

@router.get("/{id}/save")
def save(id: str, candles, session: Session = Depends(get_cassandra)):
    return save_cassandra_candles(id, candles, session)

@router.get("/{id}/last_date")
def last_date(id: str, session: Session = Depends(get_cassandra)):
    last_candle = load_candles_cassandra(id, session, 1)
    return last_candle[0][0]