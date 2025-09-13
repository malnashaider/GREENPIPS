# live/webhook_server.py
"""
Simple webhook server for TradingView alerts.
TradingView alert should send JSON like:
{
  "action": "BUY",
  "symbol": "AAPL",
  "size_pct": 1.0
}
"""
from flask import Flask, request, jsonify
import yaml
import argparse
from live.kite_executor import KiteExecutor
from live.risk_manager import RiskManager
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

cfg = None
executor = None
risk = None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info("Received webhook: %s", data)
    # Basic validation
    if not data or "action" not in data:
        return jsonify({"error":"bad payload"}), 400
    action = data["action"].upper()
    symbol = data.get("symbol", cfg.get("symbol"))
    size_pct = float(data.get("size_pct", 1.0))
    # Risk checks
    if not risk.allowed_trade(size_pct):
        return jsonify({"status":"blocked_by_risk"}), 403
    if action == "BUY":
        res = executor.place_order(symbol, "BUY", size_pct)
    elif action == "SELL":
        res = executor.place_order(symbol, "SELL", size_pct)
    else:
        return jsonify({"status":"unknown_action"}), 400
    return jsonify({"status":"ok","result":res})

def start_server(config_path):
    global cfg, executor, risk
    cfg = yaml.safe_load(open(config_path))
    executor = KiteExecutor(cfg)
    risk = RiskManager(cfg)
    app.run(host=cfg["server"]["host"], port=cfg["server"]["port"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_example.yml")
    args = ap.parse_args()
    start_server(args.config)
