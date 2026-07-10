from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import admin as admin_router
from routes import coin as coin_router
from routes import ingestion as ingestion_router

app = FastAPI(title="FastAPI PostgreSQL Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router.router, prefix="/admin", tags=["admin"])
app.include_router(coin_router.router, prefix="/coin", tags=["coin"])
app.include_router(ingestion_router.router, prefix="/ingestion", tags=["ingestion"])
