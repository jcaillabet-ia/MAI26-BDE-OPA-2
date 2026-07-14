from cassandra.cluster import Session
from fastapi import APIRouter, Depends

from dependencies import get_cassandra
from services.database import load_candles_cassandra

router = APIRouter()

@router.get("/{id}/list")
def list(id: str, session: Session = Depends(get_cassandra)):
    return load_candles_cassandra(id, session)
