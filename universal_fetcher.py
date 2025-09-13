# scripts/universal_fetcher.py
"""
Universal data fetcher for equities, indices, FX, metals, and crypto.
- Uses yfinance for equities/indices/commodities where available
- Uses CCXT for crypto tickers / exchanges
- Placeholder function for NSE option chains (requires broker/API)
"""

import pandas as pd
import time
import logging
from typing import Optional

# pip install yfinance ccxt
import yfinance as yf
import ccxt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------- Helpers --------------
def fetch_yfinance_ohlcv(symbol: str, interval: str = "15m", period: str = "30d") -> pd.DataFrame:
    """
    symbol: ticker in yfinance format, e.g., "RELIANCE.NS", "^NSEI", "GC=F" (gold futures), "EURUSD=X"
    interval: '1m','2m','5m','15m','1h','1d'
    period: "7d","30d","365d"
    """
    df = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
    if df is None or df.empty:
        logger.warning(f"No data from yfinance for {symbol} (interval={interval} period={period})")
        return pd.DataFrame()
    df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
    df.index = pd.to_datetime(df.index)
    return df[["open","high","low","close","volume"]]

# --------------- CCXT Crypto ---------------
# example: fetcher for Binance (spot)
_ccxt_exchanges = {}
def get_ccxt_exchange(name="binance"):
    if name not in _ccxt_exchanges:
        ex = getattr(ccxt, name)()
        _ccxt_exchanges[name] = ex
    return _ccxt_exchanges[name]

def fetch_crypto_ohlcv(symbol: str, exchange_name: str = "binance", timeframe: str = "15m", limit: int = 500):
    """
    symbol: "BTC/USDT", "DOGE/USDT" etc.
    timeframe: '1m','5m','15m','1h','1d'
    returns pandas DataFrame with columns open, high, low, close, volume
    """
    ex = get_ccxt_exchange(exchange_name)
    # unify symbol if needed
    try:
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    except Exception as e:
        logger.error("CCXT fetch failed: %s", e)
        return pd.DataFrame()
    df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

# --------------- NSE Option Chain Placeholder ---------------
def fetch_nse_option_chain(symbol: str):
    """
    Placeholder for fetching NSE option chain for an underlying like 'RELIANCE' or 'NIFTY'.
    Options:
    - Use Zerodha/Kite Connect instrument lookup + NSE option chain endpoints (via broker)
    - Use 'nsepython' / 'nsetools' or scrape (may break / be against TOS)
    Implement this function with your chosen provider.
    """
    raise NotImplementedError("NSE Option chain fetch requires broker API or paid data feed. Implement here.")

# --------------- Unified fetch function ---------------
def fetch_market_data(univ_symbol: str, interval: str = "15m", period: str = "30d", exchange_hint: Optional[str]=None):
    """
    univ_symbol: a canonical symbol with hints, e.g.:
      - NSE stock: "NSE:RELIANCE" -> maps to "RELIANCE.NS" for yfinance
      - BSE: "BSE:TCS" -> mapping needed
      - Index: "INDEX:NIFTY" -> "^NSEI" or other symbol
      - Crypto: "BINANCE:BTC/USDT" or "CRYPTO:BTC/USDT"
      - FX: "FX:EURUSD" -> "EURUSD=X" in yfinance or use AlphaVantage
      - Metal: "METAL:GOLD" -> "GC=F" or MCX symbol (not always in yfinance)
    """
    # simple parser:
    if univ_symbol.startswith("NSE:") or univ_symbol.endswith(".NS"):
        # convert NSE:RELIANCE -> REliance.NS
        if univ_symbol.startswith("NSE:"):
            yf_sym = univ_symbol.split(":",1)[1] + ".NS"
        else:
            yf_sym = univ_symbol
        return fetch_yfinance_ohlcv(yf_sym, interval=interval, period=period)
    if univ_symbol.startswith("BSE:"):
        # yfinance BSE tickers sometimes use .BO or .BSE - check
        yf_sym = univ_symbol.split(":",1)[1] + ".BO"
        return fetch_yfinance_ohlcv(yf_sym, interval=interval, period=period)
    if univ_symbol.startswith("INDEX:"):
        # mapping common indices
        idx = univ_symbol.split(":",1)[1].upper()
        mapping = {"NIFTY":"^NSEI","SENSEX":"^BSESN","DOW":"^DJI","SPX":"^GSPC"}
        yf_sym = mapping.get(idx, idx)
        return fetch_yfinance_ohlcv(yf_sym, interval=interval, period=period)
    if univ_symbol.startswith("BINANCE:") or univ_symbol.startswith("CRYPTO:"):
        sym = univ_symbol.split(":",1)[1]
        return fetch_crypto_ohlcv(sym, exchange_name=(exchange_hint or "binance"), timeframe=interval)
    if univ_symbol.startswith("FX:") or univ_symbol.endswith("=X"):
        # Try yfinance for FX: EURUSD -> EURUSD=X
        if univ_symbol.startswith("FX:"):
            pair = univ_symbol.split(":",1)[1].upper()
            yf_sym = f"{pair}=X"
        else:
            yf_sym = univ_symbol
        return fetch_yfinance_ohlcv(yf_sym, interval=interval, period=period)
    if univ_symbol.startswith("METAL:"):
        metal = univ_symbol.split(":",1)[1].upper()
        mapping = {"GOLD":"GC=F","SILVER":"SI=F","XAU":"GC=F"}
        yf_sym = mapping.get(metal, metal)
        return fetch_yfinance_ohlcv(yf_sym, interval=interval, period=period)

    # fallback: try direct yfinance symbol
    return fetch_yfinance_ohlcv(univ_symbol, interval=interval, period=period)


# ------------------ Example usage ------------------
if __name__ == "__main__":
    # examples:
    examples = [
        "NSE:RELIANCE",
        "BSE:TCS",
        "INDEX:NIFTY",
        "BINANCE:BTC/USDT",
        "CRYPTO:DOGE/USDT",
        "FX:EURUSD",
        "METAL:GOLD"
    ]
    for s in examples:
        print("Fetching", s)
        try:
            df = fetch_market_data(s, interval="1h", period="7d")
            print(f"{s}: rows={len(df)}")
            time.sleep(1)
        except Exception as e:
            print("Error:", e)
