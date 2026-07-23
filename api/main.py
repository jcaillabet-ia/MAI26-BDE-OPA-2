from cassandra.cluster import Cluster
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from routes import admin as admin_router
from routes import candle as candle_router
from routes import coin as coin_router
from routes import ingestion as ingestion_router
from routes import ml as ml_router

@asynccontextmanager
async def lifespan(app: FastAPI):    
    CLUSTER_IPS = ['cassandra'] 
    keyspace = "crypto_bot"
    cluster = Cluster(CLUSTER_IPS, compression=True)
    session = cluster.connect(keyspace=keyspace)
    app.state.cassandra_session = session
    yield
    cluster.shutdown()

app = FastAPI(title="API FastAPI du projet crypto-bot", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router.router, prefix="/admin", tags=["admin"])
app.include_router(candle_router.router, prefix="/candle", tags=["candle"])
app.include_router(coin_router.router, prefix="/coin", tags=["coin"])
app.include_router(ingestion_router.router, prefix="/ingestion", tags=["ingestion"])
app.include_router(ml_router.router, prefix="/ml", tags=["ml"])