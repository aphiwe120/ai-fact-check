import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

db_pool = None
try:
    db_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=20,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME")
    )
except psycopg2.OperationalError as e:
    print(f"Error: Could not connect to the database. Please check your environment variables. Details: {e}")

@contextmanager
def get_db_connection():
    """
    A context manager to get a connection from the pool.
    This will automatically handle getting a connection and putting it back.
    
    Usage:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM my_table;")
    """
    if db_pool is None:
        raise ConnectionError("Database connection pool is not available. Check initial connection.")
        
    conn = None
    try:
        conn = db_pool.getconn()
        yield conn
    finally:
        if conn:
            db_pool.putconn(conn)
                