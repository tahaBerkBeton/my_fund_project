# main.py

from fund_manager.fund_manager import (
    init_db,
    create_fund,
    buy_shares,
    sell_shares,
    get_fund_composition
)

def main():
    # Initialize the database
    init_db()
    
    fund_name = "MyFirstFund"
    print(f"Creating fund: {fund_name} with $100000 ...")
    try:
        create_fund(fund_name, 100000)
    except Exception as e:
        print(e)
    
    print("\nBuying 10 shares of AAPL ...")
    buy_shares(fund_name, "AAPL", 10)
    
    print("Buying 5 shares of TSLA ...")
    buy_shares(fund_name, "TSLA", 5)
    
    print("\nGetting current composition:")
    composition = get_fund_composition(fund_name)
    print(composition)
    
    print("\nSelling 2 shares of AAPL ...")
    sell_shares(fund_name, "AAPL", 2)
    
    print("Getting updated composition:")
    composition = get_fund_composition(fund_name)
    print(composition)

if __name__ == '__main__':
    main()
