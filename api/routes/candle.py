from cassandra.cluster import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Any

from dependencies import get_cassandra
from services.database import load_candles_cassandra, save_cassandra_candles

router = APIRouter()

class CandleInput(BaseModel):
    candles: List[Any]

@router.get("/{id}/list")
def list(id: str, session: Session = Depends(get_cassandra)):
    return load_candles_cassandra(id, session)

@router.post("/{id}/save")
def save(id: str, payload: CandleInput, session: Session = Depends(get_cassandra)):
    return save_cassandra_candles(id, payload.candles, session)

@router.get("/{id}/last_date")
def last_date(id: str, session: Session = Depends(get_cassandra)):
    last_candle = load_candles_cassandra(id, session, 1)
    return last_candle[0][0]