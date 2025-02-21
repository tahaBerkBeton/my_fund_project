
# Fund Management Project

This project provides a simple **fund/portfolio management system** in Python. It leverages:
- **SQLAlchemy** (with SQLite) for database persistence.
- **yfinance** for fetching real-time (or near real-time) market prices.
- A clearly structured Python package (`fund_manager/`) that implements:
  - Database models and utilities
  - Core fund operations (create fund, buy/sell shares, etc.)
  - Up-to-date valuations via `yfinance`

It is meant as a **starting point** for more advanced portfolio management applications and is suitable for personal finance tracking or as a teaching tool.

## Table of Contents

1. [Features](#features)  
2. [Project Structure](#project-structure)  
3. [Requirements](#requirements)  
4. [Installation and Setup](#installation-and-setup)  
5. [Running the Demo](#running-the-demo)  
6. [Usage](#usage)  
7. [Extending the Project](#extending-the-project)  
8. [License](#license)

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

---

## Project Structure

```
my_fund_project/
├── fund_manager/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── yfinance_utils.py
│   └── fund_manager.py
├── main.py
├── requirements.txt
└── README.md
```

- **`fund_manager/db.py`**: Database setup (engine/session creation).  
- **`fund_manager/models.py`**: SQLAlchemy model definitions (Funds, Positions, Valuations, Operations).  
- **`fund_manager/yfinance_utils.py`**: Helper functions to fetch live prices using `yfinance`.  
- **`fund_manager/fund_manager.py`**: Core fund operations (create, buy, sell, update, get composition).  
- **`main.py`**: Demonstrates how to use these functionalities.  
- **`requirements.txt`**: Python dependencies.  
- **`README.md`**: This file.

---

## Requirements

- **Python 3.8+** (Recommended)
- **Pip** / **Virtualenv** or **Conda** for package management

Dependencies (pinned or approximate versions can be in `requirements.txt`):
- `SQLAlchemy`
- `yfinance`
- `requests`
- `pandas`

---

## Installation and Setup

1. **Clone or download** the repository:
   ```bash
   git clone https://github.com/yourusername/my_fund_project.git
   cd my_fund_project
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Check installed packages**:
   ```bash
   pip list
   ```

---

## Running the Demo

1. **Initialize the database and perform operations**:

   ```bash
   python main.py
   ```

   The `main.py` script will:
   - Create a new SQLite database file `funds.db` (if it doesn’t exist).
   - Create a new fund named `"MyFirstFund"` with `$100000`.
   - Buy shares of AAPL and TSLA.
   - Print a snapshot of the current composition.
   - Sell some AAPL shares.
   - Print the final composition.

2. **Expected Console Output**: You should see logs/messages indicating fund creation, buy, sell, and composition retrieval, including real-time prices fetched from `yfinance`.

---

## Usage

If you want to incorporate these functionalities into your own scripts or applications, you can import them directly from `fund_manager.fund_manager`. For instance:

```python
from fund_manager.fund_manager import (
    create_fund,
    buy_shares,
    sell_shares,
    get_fund_composition
)

# Create a fund
create_fund("MyNewFund", 50000)

# Buy some stock
buy_shares("MyNewFund", "MSFT", 10)

# Sell some stock
sell_shares("MyNewFund", "MSFT", 5)

# Check current holdings
info = get_fund_composition("MyNewFund")
print(info)
```

---

## Extending the Project

Some suggested enhancements:

1. **Deposit/Withdraw Cash**: Add operations to deposit more cash into the fund or withdraw cash.  
2. **Advanced Analytics**: Track additional metrics (daily P/L, performance over time, risk metrics).  
3. **Multi-User Support**: Associate funds with specific users, add authentication, etc.  
4. **GUI or Web Interface**: Replace `main.py` with a Flask/Django/React interface for user-friendly interaction.  
5. **Batch Price Updates / Caching**: Avoid multiple `yfinance` calls in a single request, which can be slow or run into rate limits.

