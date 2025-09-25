from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class FactCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    claim: str
    status: str = Field(default="pending")  # pending, completed, error
    result: Optional[str] = Field(default=None)  # true, false, unclear, partially-true
    source_url: Optional[str] = Field(default=None)
    analysis: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./checkmate.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False in production

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")

def get_session():
    """Get a database session"""
    return Session(engine)