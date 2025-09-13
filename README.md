# AI Trading Bot — Starter Repo

Features:
- Fetch historical data (yfinance)
- Feature engineering (basic technical indicators)
- Train a simple RandomForest classifier (buy / sell / hold)
- Backtest engine (basic)
- TradingView webhook server to receive signals
- Zerodha Kite executor (example wrapper)
- Risk manager with basic checks

**IMPORTANT**: This is a starter. Always paper-test, add logging, add safety checks, and never trade real money without thorough testing.

Setup:
1. `git clone <repo>`
2. `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Edit `config_example.yml` -> save as `secrets.yml` (DO NOT push secrets to GitHub)
5. Train model: `python scripts/train.py --config config_example.yml`
6. Run webhook server: `python live/webhook_server.py --config config_example.yml`
7. # AI Trading Bot 🤖📈

An open-source **AI-powered trading bot** that:
- Learns from historical market data using ML
- Detects candlestick patterns (Hammer, Doji, Engulfing, Morning Star, etc.)
- Identifies **fake vs real breakouts** and **short/long reversals**
- Trades automatically with proper risk management
- Works with Zerodha, Groww, MT5, and TradingView integrations

---

## 🚀 Features
- AI/ML-based trade signal generation
- Full candlestick pattern detection (single, double, triple)
- Breakout & reversal filtering
- Automatic order execution via broker APIs
- Risk management (SL/TP/position sizing)
- Backtesting & paper trading support

---

## 📂 Project Structure

See code comments for more details.
