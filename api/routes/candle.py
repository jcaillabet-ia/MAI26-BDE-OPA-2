import cassandra
from cassandra.cluster import Session
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import session
from typing import List, Any

from dependencies import get_cassandra
from services.database import load_candles_cassandra, save_cassandra_candles, remove_cassandra_candles

router = APIRouter()

class CandleInput(BaseModel):
    candles: List[Any]

@router.get("/{id}/list")
def list(id: str, session: Session = Depends(get_cassandra)):
    """
    Récupère la liste des bougies pour une cryptomonnaie donnée
    """

    try:
        candles = load_candles_cassandra(id, session)
        return candles
    except cassandra.InvalidRequest:
        raise HTTPException(status_code=500, detail="La base de données Cassandra n'a pas été initialisée.")

@router.post("/{id}/save")
def save(id: str, payload: CandleInput, session: Session = Depends(get_cassandra)):
    """
    Sauvegarde les bougies pour une cryptomonnaie donnée
    """
    return save_cassandra_candles(id, payload.candles, session)

@router.get("/{coin_id}/interval")
def last_date(coin_id: str, session: Session = Depends(get_cassandra)):
    """
    Récupère l'interval ( premmier date et dernière date ) de la monnaie dont l'id est passé en paramètre.
    """

    candles = load_candles_cassandra(coin_id, session, -1)

    if not candles:
        return {"first" : None, "last" : None}

    return {"first" : candles[-1][0], "last" : candles[0][0]}

@router.delete("/{id}/remove", status_code=status.HTTP_204_NO_CONTENT)
def remove(id: str, session: Session = Depends(get_cassandra)):
    """
    Supprime les bougies présentes en base pour une crypto-monnaie donnée
    """
    return remove_cassandra_candles(id, session)