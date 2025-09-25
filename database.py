from sqlmodel import select
from models import FactCheck, get_session, create_db_and_tables
from contextlib import contextmanager
from datetime import datetime

@contextmanager
def get_db_session():
    """A context manager to handle database sessions"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_fact_check(claim: str) -> int:
    """Creates a new fact check record and returns its ID"""
    try:
        with get_db_session() as session:
            fact_check = FactCheck(claim=claim, status="pending")
            session.add(fact_check)
            session.commit()
            session.refresh(fact_check)
            print(f"✅ Fact check created with ID: {fact_check.id}")
            return fact_check.id
    except Exception as e:
        print(f"❌ Error creating fact check: {e}")
        return None

def update_fact_check(check_id: int, status: str, result: str, analysis: str):
    """Updates an existing fact check record"""
    try:
        with get_db_session() as session:
            statement = select(FactCheck).where(FactCheck.id == check_id)
            fact_check = session.exec(statement).first()
            
            if fact_check:
                fact_check.status = status
                fact_check.result = result
                fact_check.analysis = analysis
                fact_check.updated_at = datetime.utcnow()
                session.add(fact_check)
                print(f"✅ Fact check {check_id} updated successfully")
            else:
                print(f"❌ Fact check with ID {check_id} not found")
    except Exception as e:
        print(f"❌ Error updating fact check: {e}")

def get_fact_check_by_id(check_id: int) -> dict:
    """Retrieves a fact check by ID"""
    try:
        with get_db_session() as session:
            statement = select(FactCheck).where(FactCheck.id == check_id)
            fact_check = session.exec(statement).first()
            
            if fact_check:
                return {
                    "id": fact_check.id,
                    "claim": fact_check.claim,
                    "status": fact_check.status,
                    "result": fact_check.result,
                    "source_url": fact_check.source_url,
                    "analysis": fact_check.analysis,
                    "created_at": fact_check.created_at,
                    "updated_at": fact_check.updated_at
                }
            return None
    except Exception as e:
        print(f"❌ Error retrieving fact check: {e}")
        return None

def get_all_fact_checks(limit: int = 100):
    """Gets all fact checks (for admin purposes)"""
    try:
        with get_db_session() as session:
            statement = select(FactCheck).order_by(FactCheck.created_at.desc()).limit(limit)
            fact_checks = session.exec(statement).all()
            return fact_checks
    except Exception as e:
        print(f"❌ Error retrieving fact checks: {e}")
        return []