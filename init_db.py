from database import get_db_connection
import psycopg2

# --- SQL Commands to set up the database schema ---

# A function to automatically update the 'updated_at' timestamp
UPDATE_TIMESTAMP_FUNCTION = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';
"""

# The main table for storing fact-check requests and results
CREATE_FACT_CHECKS_TABLE = """
CREATE TABLE IF NOT EXISTS fact_checks (
    id SERIAL PRIMARY KEY,
    claim TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    result VARCHAR(50),
    source_url TEXT,
    analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

# A trigger to call the update function whenever a row is updated
UPDATE_TRIGGER = """
CREATE OR REPLACE TRIGGER update_fact_checks_updated_at
BEFORE UPDATE ON fact_checks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
"""

def initialize_database():
    """Connects to the database and creates the necessary tables and functions."""
    print("Attempting to initialize the database...")
    commands = [
        UPDATE_TIMESTAMP_FUNCTION,
        CREATE_FACT_CHECKS_TABLE,
        UPDATE_TRIGGER
    ]
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for command in commands:
                    cursor.execute(command)
            conn.commit()
        print("Database initialization successful. Tables and triggers are ready.")
    except (psycopg2.Error, ConnectionError) as e:
        print(f"An error occurred during database initialization: {e}")

if __name__ == "__main__":
    # This allows the script to be run directly from the command line
    # to set up the database.
    initialize_database()