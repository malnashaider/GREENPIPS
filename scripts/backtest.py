# scripts/backtest.py
import yaml
import pandas as pd
from scripts.data_fetch import fetch_ohlcv
from scripts.features import build_features_and_labels
from scripts.model import load_model
import numpy as np

def backtest(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    sym = cfg.get("symbol", "AAPL")
    interval = cfg.get("interval", "15m")
    days = cfg.get("history_days", 365)
    model_path = cfg.get("model_path", "models/rf_model.pkl")

    df = fetch_ohlcv(sym, interval=interval, days=days)
    X, y, df_all = build_features_and_labels(df)
    model = load_model(model_path)

    preds = pd.Series(model.predict(X), index=X.index)
    df_all = df_all.loc[preds.index].copy()
    df_all["pred"] = preds

    # Simple position logic: go long if pred==1, short if pred==-1 else flat
    initial_capital = 10000.0
    capital = initial_capital
    position = 0
    entry_price = 0
    capital_hist = []
    for i, row in df_all.iterrows():
        pred = row["pred"]
        price = row["close"]
        # simple position sizing: fixed fraction of capital per trade
        trade_size = capital * 0.01  # 1% per trade
        shares = trade_size / price if price>0 else 0

        # If flat and pred signals long/short -> enter
        if position == 0 and pred != 0 and shares>0:
            position = pred
            entry_price = price
        # If in position and prediction changed to hold or reversed -> close
        elif position != 0 and pred != position:
            pnl = (price - entry_price) * position * shares
            capital += pnl
            position = 0
            entry_price = 0
        capital_hist.append(capital + (position * (price - entry_price) * shares if position!=0 else 0))

    df_out = pd.DataFrame({"capital": capital_hist}, index=df_all.index[:len(capital_hist)])
    print("Start cap:", initial_capital, "End cap:", df_out["capital"].iloc[-1])
    return df_out

if __name__ == "__main__":
    import sys
    cfg = sys.argv[1] if len(sys.argv)>1 else "config_example.yml"
    backtest(cfg)
