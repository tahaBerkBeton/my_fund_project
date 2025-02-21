# fund_manager/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base

class Fund(Base):
    """
    Represents a single Fund with a unique name, current cash, etc.
    """
    __tablename__ = 'funds'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    current_cash = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)

    # Relationships
    positions = relationship("FundPosition", back_populates="fund", cascade="all, delete-orphan")
    valuations = relationship("FundValuation", back_populates="fund", cascade="all, delete-orphan")
    operations = relationship("Operation", back_populates="fund", cascade="all, delete-orphan")


class FundPosition(Base):
    """
    Stores the position (shares held) in a particular ticker for a given fund.
    """
    __tablename__ = 'fund_positions'

    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    ticker = Column(String, nullable=False)
    shares_held = Column(Float, default=0.0)
    last_purchase_price = Column(Float, default=0.0)
    last_purchase_date = Column(DateTime, default=datetime.utcnow)

    fund = relationship("Fund", back_populates="positions")


class FundValuation(Base):
    """
    Tracks historical valuations of a fund each time an update is done.
    """
    __tablename__ = 'fund_valuations'

    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    valuation_date = Column(DateTime, default=datetime.utcnow)
    total_value = Column(Float, default=0.0)

    fund = relationship("Fund", back_populates="valuations")


class Operation(Base):
    """
    Logs all operations on a fund (CREATE, BUY, SELL, etc.) for audit/history.
    """
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    ticker = Column(String, nullable=True)  # might be empty for 'CREATE' or other ops
    operation_type = Column(String, nullable=False)  # e.g., CREATE, BUY, SELL
    shares = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    operation_date = Column(DateTime, default=datetime.utcnow)

    fund = relationship("Fund", back_populates="operations")
