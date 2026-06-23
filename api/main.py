from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import coin as coin_router

app = FastAPI(title="FastAPI PostgreSQL Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coin_router.router, prefix="/coin", tags=["coin"])