from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import coin as coin_router
from routes import site as site_router

app = FastAPI(title="FastAPI PostgreSQL Bridge")
app.include_router(coin_router.router, prefix="/coin", tags=["coin"])
app.include_router(site_router.router, tags=["site"])
app.mount("/static", StaticFiles(directory="static"), name="static")