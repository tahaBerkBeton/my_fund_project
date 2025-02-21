# main.py

from fund_manager.fund_manager import (
    init_db,
    create_fund,
    buy_shares,
    sell_shares,
    get_fund_composition
)

def main():
    # Initialize the database (create tables if not exist)
    init_db()

    fund_name = "MyFirstFund"
    print(f"Creating fund: {fund_name} with $100000 ...")
    create_fund(fund_name, 100000)

    print("\nBuying 10 shares of AAPL ...")
    buy_shares(fund_name, "AAPL", 10)

    print("Buying 5 shares of TSLA ...")
    buy_shares(fund_name, "TSLA", 5)

    print("\nGetting current composition:")
    composition_1 = get_fund_composition(fund_name)
    print(composition_1)

    print("\nSelling 2 shares of AAPL ...")
    sell_shares(fund_name, "AAPL", 2)

    print("Getting updated composition:")
    composition_2 = get_fund_composition(fund_name)
    print(composition_2)


if __name__ == "__main__":
    main()
