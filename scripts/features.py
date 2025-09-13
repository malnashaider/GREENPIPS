# scripts/features.py
import pandas as pd
import numpy as np
import ta  # technical indicators library

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi14"] = ta.momentum.rsi(df["close"], window=14)
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()
    df["atr14"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)
    df["returns"] = df["close"].pct_change()
    df = df.dropna()
    return df

def build_features_and_labels(df: pd.DataFrame, future_bars: int = 3, threshold: float = 0.001):
    """
    Build features and a 3-class label: 1=long, -1=short, 0=hold based on future returns.
    threshold = minimum return to consider an actionable signal.
    """
    df = add_technical_indicators(df)
    df["future_return"] = df["close"].shift(-future_bars) / df["close"] - 1.0
    def label(r):
        if r > threshold:
            return 1
        elif r < -threshold:
            return -1
        else:
            return 0
    df["label"] = df["future_return"].apply(lambda x: label(x) if pd.notnull(x) else 0)
    feature_cols = ["close","volume","rsi14","ma20","ma50","atr14","returns"]
    X = df[feature_cols].dropna()
    y = df.loc[X.index, "label"]
    return X, y, df
