# fund_manager/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLAlchemy base class
Base = declarative_base()

def get_engine():
    """
    Returns a SQLAlchemy engine, pointing to a local SQLite database.
    Adjust the connection string for your environment as needed.
    """
    return create_engine("sqlite:///funds.db", echo=False)

def get_session():
    """
    Returns a new SQLAlchemy session object.
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
