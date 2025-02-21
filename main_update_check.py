# main_update_check.py

import time
from fund_manager.fund_manager import init_db, update_all_funds
from fund_manager.db import get_session
from fund_manager.models import Fund, FundValuation

def get_last_valuation_timestamp(fund_id, session):
    """
    Returns the latest valuation timestamp for the given fund.
    """
    valuation = (
        session.query(FundValuation)
        .filter_by(fund_id=fund_id)
        .order_by(FundValuation.valuation_date.desc())
        .first()
    )
    return valuation.valuation_date if valuation else None

def check_new_valuation():
    session = get_session()
    try:
        # Retrieve each fund's last valuation timestamp before the update.
        funds = session.query(Fund).all()
        before_timestamps = {}
        print("=== Before Update ===")
        for fund in funds:
            last_ts = get_last_valuation_timestamp(fund.id, session)
            before_timestamps[fund.id] = last_ts
            print(f"Fund: {fund.name} | Last Valuation Timestamp: {last_ts}")
        
        # Wait briefly to ensure the new timestamps will differ.
        time.sleep(2)
        
        # Update all funds (each update adds a new valuation record).
        print("\nUpdating all funds...\n")
        update_all_funds()
        
        # Retrieve and display updated timestamps.
        print("=== After Update ===")
        funds = session.query(Fund).all()  # re-query to get latest data
        for fund in funds:
            new_ts = get_last_valuation_timestamp(fund.id, session)
            print(f"Fund: {fund.name} | New Last Valuation Timestamp: {new_ts}")
            if before_timestamps[fund.id] is None:
                print(f"  -> No valuation existed before. New record added at {new_ts}")
            elif new_ts > before_timestamps[fund.id]:
                print(f"  -> New valuation record appended at {new_ts}")
            else:
                print("  -> No new valuation record detected.")
    finally:
        session.close()

def main():
    init_db()
    check_new_valuation()

if __name__ == '__main__':
    main()
