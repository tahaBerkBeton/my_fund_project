# fund_manager/yfinance_utils.py

import yfinance as yf

def fetch_live_price(ticker: str) -> float:
    """
    Fetches the current market price for a given ticker using yfinance.
    Returns the last available Close price.
    """
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period="1d")
    if df.empty:
        raise ValueError(f"No market data returned for ticker: {ticker}")
    last_close = df['Close'][-1]
    return float(last_close)
