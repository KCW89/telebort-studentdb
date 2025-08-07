"""
Base database configuration and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Determine environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Database configuration
if ENVIRONMENT == 'production':
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/telebort_studentdb')
else:
    # Use SQLite for development
    DATABASE_URL = 'sqlite:///telebort_studentdb.db'

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()