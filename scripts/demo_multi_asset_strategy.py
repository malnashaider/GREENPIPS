# scripts/demo_multi_asset_strategy.py
"""
Demo multi-asset strategy:
- Loads instrument_registry.csv
- Fetches OHLCV via universal_fetcher.fetch_market_data()
- Uses candlestick 'final_signal' + simple MA crossover as a proxy for AI signal
- Prints suggested trades with size_pct (paper mode)

Usage:
python scripts/demo_multi_asset_strategy.py
"""

import csv
import time
import logging
from pathlib import Path
from universal_fetcher import fetch_market_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("data/instrument_registry.csv")
DEFAULT_INTERVAL = "15m"
DEFAULT_PERIOD = "7d"

def simple_ma_signal(df, fast=8, slow=21):
    """Return 1 if fast MA > slow MA, -1 if reverse, else 0"""
    if df is None or df.empty or len(df) < slow+2:
        return 0
    close = df["close"]
    ma_fast = close.rolling(fast).mean().iloc[-1]
    ma_slow = close.rolling(slow).mean().iloc[-1]
    if ma_fast > ma_slow:
        return 1
    elif ma_fast < ma_slow:
        return -1
    else:
        return 0

def compute_size_pct(config_capital=100000, risk_per_trade_pct=1.0):
    """Simple fixed size for demo. Real: compute via ATR or margin."""
    return min(2.0, risk_per_trade_pct)  # return percent

def run_demo():
    if not REGISTRY_PATH.exists():
        logger.error("Registry file missing: %s", REGISTRY_PATH)
        return
    suggested_trades = []
    with open(REGISTRY_PATH) as f:
        reader = csv.reader([row for row in f if row.strip() and not row.strip().startswith("#")])
        for row in reader:
            try:
                uni_sym = row[0].strip()
            except Exception:
                continue
            logger.info("Fetching %s", uni_sym)
            df = fetch_market_data(uni_sym, interval=DEFAULT_INTERVAL, period=DEFAULT_PERIOD)
            if df is None or df.empty:
                logger.warning("No data for %s", uni_sym)
                continue
            # Use candlestick final_signal if present
            final_signal = 0
            if "final_signal" in df.columns:
                final_signal = int(df["final_signal"].iloc[-1])
            # AI proxy: simple MA crossover
            ai_signal = simple_ma_signal(df)
            # Combine rules: require AI + candle agreement to act
            combined = 0
            if ai_signal == final_signal and ai_signal != 0:
                combined = ai_signal
            else:
                # Less strict option: take majority or weighted
                if ai_signal != 0 and final_signal != 0 and ai_signal == final_signal:
                    combined = ai_signal
                elif ai_signal != 0 and final_signal == 0:
                    combined = ai_signal  # allow AI-only
                elif final_signal != 0 and ai_signal == 0:
                    combined = final_signal  # allow pattern-only in demo

            if combined != 0:
                suggested_trades.append({
                    "symbol": uni_sym,
                    "side": "BUY" if combined==1 else "SELL",
                    "size_pct": compute_size_pct(),
                    "reason": f"ai={ai_signal},candle={final_signal}"
                })
            time.sleep(0.5)  # polite pause to avoid rate limits

    logger.info("Suggested trades (paper):")
    for t in suggested_trades:
        logger.info(t)
    print("Total suggestions:", len(suggested_trades))
    return suggested_trades

if __name__ == "__main__":
    run_demo()
