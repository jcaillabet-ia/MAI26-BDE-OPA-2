import os
import psycopg2

def open_connection():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
    
    return psycopg2.connect(database_url, connect_timeout=5)