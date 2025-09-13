# live/kite_executor.py
"""
Wrapper for Zerodha KiteConnect. NOTE: store secrets outside source control.
You must pip install kiteconnect and provide api_key/access_token in secrets.
"""
from kiteconnect import KiteConnect
import yaml
import logging

logger = logging.getLogger(__name__)

class KiteExecutor:
    def __init__(self, cfg):
        self.cfg = cfg
        kc_cfg = cfg.get("zerodha", {})
        api_key = kc_cfg.get("api_key")
        access_token = kc_cfg.get("access_token")
        if not api_key or not access_token:
            logger.warning("Kite API key or access token missing. Executor will be in paper mode.")
            self.kite = None
            return
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def place_order(self, symbol, side, size_pct=1.0):
        """
        Very simple: calculates quantity from size_pct of account. For demo only.
        You must implement proper qty calculation, instrument token lookup, error handling.
        """
        if not self.kite:
            logger.info(f"PAPER: would {side} {symbol} size_pct={size_pct}")
            return {"paper": True, "action": side, "symbol": symbol}
        # TODO: look up margin / balance to translate size_pct -> qty
        try:
            # This is a placeholder. You need to find instrument_token or tradingsymbol etc.
            order = self.kite.place_order(
                tradingsymbol=symbol,
                exchange="NSE",
                transaction_type="BUY" if side=="BUY" else "SELL",
                quantity=1,
                order_type="MARKET",
                product="MIS"
            )
            return order
        except Exception as e:
            logger.exception("Order failed")
            return {"error": str(e)}
