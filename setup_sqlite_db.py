from models import create_db_and_tables

if __name__ == "__main__":
    print("🔄 Setting up SQLite database...")
    create_db_and_tables()
    print("✅ Database setup completed!")