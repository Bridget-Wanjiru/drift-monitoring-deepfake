"""
Database Configuration
Handles secure connection pool management to Neon Cloud PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator # <-- ADD THIS IMPORT

# Load variables from root .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(" DATABASE_URL missing from your root .env file!")

# Enforce secure cloud parameters natively
if "sslmode=require" not in DATABASE_URL:
    DATABASE_URL += "&sslmode=require" if "?" in DATABASE_URL else "?sslmode=require"

# Create a clean engine with production-ready connection pool sizes
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """Provides a transactional database session context."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_connection() -> bool:
    """Verifies that the local engine can authenticate with Neon."""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1;"))
        print("✓ Database connection fully authenticated with Neon Cloud!")
        return True
    except Exception as e:
        print(f"✗ Database connection configuration error: {e}")
        return False

if __name__ == "__main__":
    verify_connection()