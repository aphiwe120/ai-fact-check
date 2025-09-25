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

def get_fact_check_by_id(check_id):
    """
    Retrieves a single fact-check record from the database by its ID.
    Returns a dictionary representing the record, or None if not found.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, claim, status, result, source_url, analysis, created_at, updated_at FROM fact_checks WHERE id = %s",
                    (check_id,) # The comma is important to make it a tuple
                )
                record = cursor.fetchone()
                if record:
                    # Get column names from the cursor description
                    columns = [desc[0] for desc in cursor.description]
                    # Return the record as a dictionary
                    return dict(zip(columns, record))
                return None # No record found with that ID
    except (psycopg2.Error, ConnectionError) as e:
        print(f"Error retrieving fact-check with id {check_id}: {e}")
        return None                