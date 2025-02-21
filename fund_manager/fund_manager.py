# fund_manager/fund_manager.py

from datetime import datetime
from sqlalchemy.exc import IntegrityError

from .db import get_session, get_engine, Base
from .models import Fund, FundPosition, FundValuation, Operation
from .yfinance_utils import fetch_live_price


def init_db():
    """
    Creates all tables (if they do not exist). Call this once on startup.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)


def create_fund(fund_name, initial_cash):
    """
    Creates a new fund with the given name and starting cash.
    Raises ValueError if a fund with the name already exists.
    """
    session = get_session()
    try:
        new_fund = Fund(
            name=fund_name,
            current_cash=initial_cash
        )
        session.add(new_fund)
        session.commit()

        # Log creation operation
        op = Operation(
            fund_id=new_fund.id,
            operation_type="CREATE",
            shares=0.0,
            price=0.0
        )
        session.add(op)

        # Log initial valuation
        val = FundValuation(
            fund_id=new_fund.id,
            total_value=initial_cash
        )
        session.add(val)
        session.commit()

    except IntegrityError:
        session.rollback()
        raise ValueError(f"Fund with name '{fund_name}' already exists.")
    finally:
        session.close()


def buy_shares(fund_name, ticker, num_shares):
    """
    Buys `num_shares` of `ticker` for the specified fund.
    Deducts from fund's cash and updates position.
    Raises ValueError if insufficient cash or fund not found.
    """
    session = get_session()
    try:
        fund = session.query(Fund).filter_by(name=fund_name).one_or_none()
        if not fund:
            raise ValueError(f"Fund {fund_name} does not exist.")

        # Fetch current market price
        current_price = fetch_live_price(ticker)
        total_cost = current_price * num_shares

        if fund.current_cash < total_cost:
            raise ValueError(
                f"Insufficient cash in fund {fund_name}. "
                f"Needed {total_cost}, available {fund.current_cash}."
            )

        # Deduct the cost
        fund.current_cash -= total_cost

        # Update or create position
        position = session.query(FundPosition).filter_by(
            fund_id=fund.id,
            ticker=ticker
        ).one_or_none()

        if not position:
            position = FundPosition(
                fund_id=fund.id,
                ticker=ticker,
                shares_held=num_shares,
                last_purchase_price=current_price,
                last_purchase_date=datetime.utcnow()
            )
            session.add(position)
        else:
            # Example approach: Weighted-average the last_purchase_price
            total_existing_value = position.shares_held * position.last_purchase_price
            total_new_value = num_shares * current_price
            new_shares_sum = position.shares_held + num_shares

            if new_shares_sum > 0:
                weighted_price = (total_existing_value + total_new_value) / new_shares_sum
            else:
                weighted_price = current_price  # fallback in extreme case

            position.shares_held += num_shares
            position.last_purchase_price = weighted_price
            position.last_purchase_date = datetime.utcnow()

        # Log the BUY operation
        op = Operation(
            fund_id=fund.id,
            ticker=ticker,
            operation_type="BUY",
            shares=num_shares,
            price=current_price
        )
        session.add(op)

        fund.last_update = datetime.utcnow()
        session.commit()
    finally:
        session.close()


def sell_shares(fund_name, ticker, num_shares):
    """
    Sells `num_shares` of `ticker` from the specified fund.
    Adds proceeds to fund's cash and updates position.
    Raises ValueError if insufficient shares or fund not found.
    """
    session = get_session()
    try:
        fund = session.query(Fund).filter_by(name=fund_name).one_or_none()
        if not fund:
            raise ValueError(f"Fund {fund_name} does not exist.")

        position = session.query(FundPosition).filter_by(
            fund_id=fund.id,
            ticker=ticker
        ).one_or_none()
        if not position or position.shares_held < num_shares:
            available = position.shares_held if position else 0
            raise ValueError(
                f"Cannot sell {num_shares} shares. Only {available} available."
            )

        # Fetch current market price
        current_price = fetch_live_price(ticker)
        proceeds = current_price * num_shares

        # Update position and fund
        position.shares_held -= num_shares
        fund.current_cash += proceeds

        # Log the SELL operation
        op = Operation(
            fund_id=fund.id,
            ticker=ticker,
            operation_type="SELL",
            shares=num_shares,
            price=current_price
        )
        session.add(op)

        fund.last_update = datetime.utcnow()
        session.commit()
    finally:
        session.close()


def update_fund(fund_name):
    """
    Explicitly updates the fund by fetching the latest prices
    and storing a snapshot in fund_valuations.
    """
    session = get_session()
    try:
        fund = session.query(Fund).filter_by(name=fund_name).one_or_none()
        if not fund:
            raise ValueError(f"Fund {fund_name} does not exist.")

        total_value = fund.current_cash
        positions = session.query(FundPosition).filter_by(fund_id=fund.id).all()

        for pos in positions:
            if pos.shares_held > 0:
                price = fetch_live_price(pos.ticker)
                total_value += price * pos.shares_held

        # Create a new valuation record
        valuation = FundValuation(
            fund_id=fund.id,
            total_value=total_value
        )
        session.add(valuation)

        fund.last_update = datetime.utcnow()
        session.commit()
    finally:
        session.close()


def update_all_funds():
    """
    Updates all funds in the database by fetching the latest prices for each position
    and creating a valuation snapshot for each fund.
    """
    session = get_session()
    try:
        funds = session.query(Fund).all()
        for fund in funds:
            total_value = fund.current_cash
            positions = session.query(FundPosition).filter_by(fund_id=fund.id).all()
            for pos in positions:
                if pos.shares_held > 0:
                    price = fetch_live_price(pos.ticker)
                    total_value += price * pos.shares_held

            # Create a new valuation record for this fund
            valuation = FundValuation(
                fund_id=fund.id,
                total_value=total_value
            )
            session.add(valuation)
            fund.last_update = datetime.utcnow()

        session.commit()
    finally:
        session.close()


def get_fund_composition(fund_name):
    """
    Returns a dict with up-to-date info about the fund's composition.
    Internally calls update_fund to ensure we have a fresh snapshot.
    """
    # Update the fund first to record historical snapshot
    update_fund(fund_name)

    session = get_session()
    try:
        fund = session.query(Fund).filter_by(name=fund_name).one_or_none()
        if not fund:
            raise ValueError(f"Fund {fund_name} does not exist.")

        composition = []
        total_value = fund.current_cash

        positions = session.query(FundPosition).filter_by(fund_id=fund.id).all()
        for pos in positions:
            if pos.shares_held > 0:
                current_price = fetch_live_price(pos.ticker)
                market_val = current_price * pos.shares_held
                total_value += market_val

                composition.append({
                    "ticker": pos.ticker,
                    "shares_held": pos.shares_held,
                    "market_price": current_price,
                    "last_purchase_price": pos.last_purchase_price,
                    "last_purchase_date": pos.last_purchase_date,
                    "market_value": market_val
                })

        return {
            "fund_name": fund.name,
            "cash": fund.current_cash,
            "positions": composition,
            "total_value": total_value
        }
    finally:
        session.close()
