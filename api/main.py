from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import admin as admin_router

app = FastAPI(title="FastAPI PostgreSQL Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router.router, prefix="/admin", tags=["admin"])