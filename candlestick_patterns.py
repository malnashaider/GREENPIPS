"""
candlestick_patterns.py
--------------------------------
Detects single, double, and triple candlestick patterns.
Works on any timeframe OHLCV data.
"""

import pandas as pd


def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect candlestick patterns.
    Input: DataFrame with ['open','high','low','close']
    Output: DataFrame with pattern columns + final signal
    """
    df = df.copy()

    o, h, l, c = df["open"], df["high"], df["low"], df["close"]

    # --------------- Single Candle Patterns ---------------

    # Hammer (bullish bottom reversal)
    df["hammer"] = ((c > o) &
                    ((o - l) >= 2 * abs(c - o)) &
                    ((h - c) <= abs(c - o))).astype(int)

    # Inverted Hammer (bullish bottom reversal)
    df["inverted_hammer"] = ((c > o) &
                             ((h - c) >= 2 * abs(c - o)) &
                             ((o - l) <= abs(c - o))).astype(int)

    # Hanging Man (bearish top reversal, same as hammer but after uptrend)
    df["hanging_man"] = ((o > c) &
                         ((o - l) >= 2 * abs(c - o)) &
                         ((h - o) <= abs(c - o))).astype(int) * -1

    # Shooting Star (bearish top reversal)
    df["shooting_star"] = ((o > c) &
                           ((h - o) >= 2 * abs(c - o)) &
                           ((c - l) <= abs(c - o))).astype(int) * -1

    # Doji (indecision)
    df["doji"] = (abs(c - o) <= 0.001 * c).astype(int)

    # Dragonfly Doji (bullish at support)
    df["dragonfly_doji"] = ((abs(c - o) <= 0.001 * c) &
                            ((h - max(c, o)) <= (c * 0.001)) &
                            ((min(c, o) - l) >= (abs(c - o) * 2))).astype(int)

    # Gravestone Doji (bearish at resistance)
    df["gravestone_doji"] = ((abs(c - o) <= 0.001 * c) &
                             ((max(c, o) - l) <= (c * 0.001)) &
                             ((h - max(c, o)) >= (abs(c - o) * 2))).astype(int) * -1

    # Spinning Top (indecision)
    df["spinning_top"] = (((h - l) > 3 * abs(c - o)) &
                          ((c - l) / (0.001 + h - l) > 0.3) &
                          ((h - c) / (0.001 + h - l) > 0.3)).astype(int)

    # Marubozu (strong trend candle, no wicks)
    df["marubozu_bull"] = ((c > o) & ((h == c) & (l == o))).astype(int)
    df["marubozu_bear"] = ((o > c) & ((h == o) & (l == c))).astype(int) * -1

    # --------------- Double Candle Patterns ---------------

    # Bullish Engulfing
    df["bull_engulf"] = ((c > o) &
                         (c.shift(1) < o.shift(1)) &
                         (c > o.shift(1)) &
                         (o < c.shift(1))).astype(int)

    # Bearish Engulfing
    df["bear_engulf"] = ((c < o) &
                         (c.shift(1) > o.shift(1)) &
                         (c < o.shift(1)) &
                         (o > c.shift(1))).astype(int) * -1

    # Piercing Pattern (bullish reversal)
    df["piercing"] = ((c > o) &
                      (c.shift(1) < o.shift(1)) &
                      (c > (o.shift(1) + c.shift(1)) / 2) &
                      (o < c.shift(1))).astype(int)

    # Dark Cloud Cover (bearish reversal)
    df["dark_cloud"] = ((c < o) &
                        (c.shift(1) > o.shift(1)) &
                        (c < (o.shift(1) + c.shift(1)) / 2) &
                        (o > c.shift(1))).astype(int) * -1

    # Tweezer Bottoms (bullish)
    df["tweezer_bottom"] = ((c > o) &
                            (c.shift(1) < o.shift(1)) &
                            (abs(l - l.shift(1)) <= 0.002 * l)).astype(int)

    # Tweezer Tops (bearish)
    df["tweezer_top"] = ((c < o) &
                         (c.shift(1) > o.shift(1)) &
                         (abs(h - h.shift(1)) <= 0.002 * h)).astype(int) * -1

    # --------------- Triple Candle Patterns ---------------

    # Morning Star (bullish 3-candle reversal)
    df["morning_star"] = ((c.shift(2) < o.shift(2)) &
                          (abs(c.shift(1) - o.shift(1)) <= 0.002 * c.shift(1)) &
                          (c > (o.shift(2) + c.shift(2)) / 2)).astype(int)

    # Evening Star (bearish 3-candle reversal)
    df["evening_star"] = ((c.shift(2) > o.shift(2)) &
                          (abs(c.shift(1) - o.shift(1)) <= 0.002 * c.shift(1)) &
                          (c < (o.shift(2) + c.shift(2)) / 2)).astype(int) * -1

    # Three White Soldiers (bullish continuation)
    df["three_white_soldiers"] = ((c > o) &
                                  (c.shift(1) > o.shift(1)) &
                                  (c.shift(2) > o.shift(2)) &
                                  (c > c.shift(1)) &
                                  (c.shift(1) > c.shift(2))).astype(int)

    # Three Black Crows (bearish continuation)
    df["three_black_crows"] = ((c < o) &
                               (c.shift(1) < o.shift(1)) &
                               (c.shift(2) < o.shift(2)) &
                               (c < c.shift(1)) &
                               (c.shift(1) < c.shift(2))).astype(int) * -1

    # Three Inside Up (bullish reversal)
    df["three_inside_up"] = ((c.shift(1) > o.shift(1)) &
                             (o.shift(1) < c.shift(2)) &
                             (c.shift(1) > o.shift(2)) &
                             (c > c.shift(1))).astype(int)

    # Three Inside Down (bearish reversal)
    df["three_inside_down"] = ((c.shift(1) < o.shift(1)) &
                               (o.shift(1) > c.shift(2)) &
                               (c.shift(1) < o.shift(2)) &
                               (c < c.shift(1))).astype(int) * -1

    # --------------- Final Signal ---------------
    pattern_cols = [col for col in df.columns if col not in ["open", "high", "low", "close", "volume"]]
    df["final_signal"] = df[pattern_cols].sum(axis=1)

    return df


# ------------------ Example Usage ------------------
if __name__ == "__main__":
    data = {
        "open": [100, 102, 104, 103, 105, 108, 110],
        "high": [103, 105, 106, 106, 108, 112, 113],
        "low": [98, 101, 102, 101, 104, 107, 109],
        "close": [102, 104, 103, 105, 107, 111, 112],
        "volume": [1500, 1600, 1700, 1650, 1800, 2000, 2100]
    }
    df = pd.DataFrame(data)
    result = detect_patterns(df)
    print(result[["open","high","low","close","final_signal"]])
