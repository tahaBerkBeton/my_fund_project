# test_insufficient_cash.py

from fund_manager.fund_manager import init_db, create_fund, buy_shares, get_fund_composition

def main():
    # Initialize the database and create a fund with limited cash.
    init_db()
    fund_name = "TestInsufficientCashFund"
    try:
        create_fund(fund_name, 1000)
        print(f"Fund '{fund_name}' created with $1000.")
    except Exception as e:
        print(e)
    
    # Attempt to buy 10 shares of AAPL (which should exceed the available cash).
    print("\nAttempting to buy 10 shares of AAPL with insufficient cash...")
    try:
        buy_shares(fund_name, "AAPL", 10)
    except Exception as e:
        print("Caught error:", e)
    
    # Display the fund composition to confirm no shares were purchased.
    print("\nCurrent Fund Composition:")
    composition = get_fund_composition(fund_name)
    print(composition)

if __name__ == '__main__':
    main()
