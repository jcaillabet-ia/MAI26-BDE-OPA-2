import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine, text, select
from models import Coin, Ticker, CoinTicker

from routes import coin as coin_router

app = FastAPI(title="FastAPI PostgreSQL Bridge")

# Récupérer l'URL de connexion depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

# Configuration de l'engine SQLModel
engine = create_engine(DATABASE_URL, echo=True)

# Configuration de Jinja2
templates = Jinja2Templates(directory="templates")

# Configuration des fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(coin_router.router, prefix="/coin", tags=["coin"])

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    # Récupérer la liste des coins de la base de données
    coins = session.exec(select(Coin).order_by(Coin.market_cap.desc()).limit(100)).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"coins": coins}
    )