from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Create the SQLAlchemy engine. We configure it to support PostgreSQL or local SQLite.
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    # Standard connection pool configurations
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency to inject database sessions into path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
