
# Fund Management Project

This project provides a simple **fund/portfolio management system** in Python. It leverages:
- **SQLAlchemy** (with SQLite) for database persistence.
- **yfinance** for fetching real-time (or near real-time) market prices.
- A clearly structured Python package (`fund_manager/`) that implements:
  - Database models and utilities.
  - Core fund operations (create fund, buy/sell shares, update valuations, bulk update funds).
  - Up-to-date valuations via `yfinance`.

It is meant as a **starting point** for more advanced portfolio management applications and is suitable for personal finance tracking or as a teaching tool.

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Requirements](#requirements)
4. [Installation and Setup](#installation-and-setup)
5. [Running the Demo](#running-the-demo)
6. [Usage](#usage)
7. [Testing and Visualization](#testing-and-visualization)
8. [Extending the Project](#extending-the-project)
9. [License](#license)

---

## Features

1. **Fund Creation**: Create a new fund with an initial cash balance.
2. **Buy and Sell Operations**:  
   - **Buy** shares of a stock using the fund’s cash.  
   - **Sell** shares, adding proceeds to the fund’s cash balance.
3. **Real-Time Valuation**: Fetch stock prices on demand via `yfinance`.
4. **Historical Tracking**:
   - **Operations**: Each buy, sell, or creation is logged in the database.
   - **Valuations**: Each time the fund is updated or queried, a snapshot is stored.
5. **Composition Retrieval**: Get the latest fund composition (holdings, prices, cash, total value).
6. **Bulk Update**: Update all funds at once using `update_all_funds()`, which appends a new valuation record for each fund.
7. **Error Handling**: Prevents transactions (e.g., buying shares) when there is insufficient cash.
8. **Visualization**: Scripts are provided to plot the valuation history of each fund over time.

---

## Project Structure

```
my_fund_project/
├── fund_manager/
│   ├── __init__.py
│   ├── db.py                 # Database setup: engine and session creation.
│   ├── models.py             # SQLAlchemy model definitions (Funds, Positions, Valuations, Operations).
│   ├── yfinance_utils.py     # Helper functions to fetch live stock prices using yfinance.
│   └── fund_manager.py       # Core fund operations: create fund, buy, sell, update, update all funds, get composition.
├── main.py                   # Demonstrates basic fund operations.
├── main_update_check.py      # Updates all funds and verifies new valuation records are appended.
├── plot_valuations.py        # Plots a time series curve of fund valuations using matplotlib.
├── test_insufficient_cash.py # Tests error handling when attempting to buy with insufficient cash.
├── requirements.txt          # Python dependencies.
└── README.md                 # This file.
```

---

## Requirements

- **Python 3.8+** (Recommended)
- **Pip** / **Virtualenv** or **Conda** for package management

Dependencies (as listed in `requirements.txt`):
- `SQLAlchemy`
- `yfinance`
- `requests`
- `pandas`
- `matplotlib` (for visualization)

---

## Installation and Setup

1. **Clone or download** the repository:
   ```bash
   git clone [https://github.com/yourusername/my_fund_project.git](https://github.com/tahaBerkBeton/my_fund_project.git)
   cd my_fund_project
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or on Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Verify installation**:
   ```bash
   pip list
   ```

---

## Running the Demo

1. **Basic Fund Operations**:  
   Initialize the database and perform basic operations:
   ```bash
   python main.py
   ```
   - This script will:
     - Create a new fund named `"MyFirstFund"` with `$100000`.
     - Buy shares of AAPL and TSLA.
     - Display the current fund composition.
     - Sell some shares.
     - Display the updated fund composition.

2. **Bulk Update and Valuation Check**:  
   Update all funds at once and verify that new valuation records are appended:
   ```bash
   python main_update_check.py
   ```
   - This script prints the last valuation timestamp before and after updating all funds.

3. **Visualization**:  
   Plot the valuation history for each fund:
   ```bash
   python plot_valuations.py
   ```
   - A matplotlib window will open showing the evolution of each fund's total value over time.

4. **Testing Error Handling**:  
   Test what happens when trying to buy shares with insufficient cash:
   ```bash
   python test_insufficient_cash.py
   ```
   - This script attempts to execute a buy order that exceeds available cash and verifies that an appropriate error is raised.

---

## Usage

To integrate or use the core functionalities in your own application, import them directly from `fund_manager.fund_manager`. For example:

```python
from fund_manager.fund_manager import (
    create_fund,
    buy_shares,
    sell_shares,
    get_fund_composition,
    update_all_funds
)

# Create a fund
create_fund("MyNewFund", 50000)

# Buy some stock
buy_shares("MyNewFund", "MSFT", 10)

# Sell some stock
sell_shares("MyNewFund", "MSFT", 5)

# Bulk update all funds (appending a new valuation record for each)
update_all_funds()

# Retrieve the current composition
composition = get_fund_composition("MyNewFund")
print(composition)
```

All operations, including error handling and real-time updates via `yfinance`, are seamlessly managed by the framework.

---

## Testing and Visualization

The project includes several scripts for testing and visualization:

- **`test_insufficient_cash.py`**: Tests error handling by attempting to buy shares with insufficient cash.
- **`main_update_check.py`**: Updates all funds and prints before-and-after timestamps of the valuation snapshots.
- **`plot_valuations.py`**: Visualizes the historical valuation of each fund as a time series curve using matplotlib.

---

## Extending the Project

Potential enhancements include:

1. **Deposit/Withdraw Cash**: Implement operations to deposit additional cash or withdraw funds.
2. **Advanced Analytics**: Track metrics like daily profit/loss, performance percentages, and risk measures.
3. **Multi-User Support**: Extend the framework to support multiple users with authentication and user-specific funds.
4. **GUI or Web Interface**: Develop a desktop or web application interface (using frameworks like Flask, Django, or React) for a more user-friendly experience.
5. **Performance Enhancements**: Implement batch processing, caching, or asynchronous updates to reduce reliance on frequent external API calls.

