# scripts/data_fetch.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_ohlcv(symbol: str, interval: str = "15m", days: int = 365):
    """
    Uses yfinance to fetch data. For Indian NSE tickers use e.g. "TCS.NS"
    interval examples: "1m","5m","15m","1h","1d"
    """
    period_days = days
    period = f"{period_days}d"
    df = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError("No data fetched — check symbol/interval")
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
    })
    df.index = pd.to_datetime(df.index)
    return df[["open", "high", "low", "close", "volume"]]
