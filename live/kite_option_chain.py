# live/kite_option_chain.py
"""
Kite Connect example:
- list instruments (large CSV) and filter option chain for an underlying
- fetch LTP/quotes for option instruments
- simple place_order example (paper/demo if no keys provided)

Requirements:
pip install kiteconnect
"""

import os
import logging
from kiteconnect import KiteConnect
from typing import List, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class KiteHelper:
    def __init__(self, api_key=None, access_token=None):
        api_key = api_key or os.getenv("KITE_API_KEY")
        access_token = access_token or os.getenv("KITE_ACCESS_TOKEN")
        if not api_key:
            logger.warning("No KITE_API_KEY provided — KiteHelper will be in PAPER mode")
            self.kite = None
            return
        self.kite = KiteConnect(api_key=api_key)
        if access_token:
            self.kite.set_access_token(access_token)

    def load_instruments(self):
        """
        Downloads the full instrument list from Kite (may be large).
        Returns list of dicts. This call may be heavy; cache results locally.
        """
        if not self.kite:
            raise RuntimeError("Kite not initialized")
        logger.info("Downloading instruments (may take a while)...")
        instruments = self.kite.instruments()  # returns list of dicts
        return instruments

    def filter_option_chain(self, instruments: List[Dict], underlying: str, expiry: str = None, strike_window: int = 10):
        """
        Filter instrument list to option contracts for an underlying.
        underlying: e.g., 'RELIANCE' or 'NIFTY'
        expiry: exact date string '2025-09-25' or None to include all
        strike_window: number of strikes around ATM to return (requires you compute/choose ATM)
        Returns list of instrument dicts matching underlying.
        """
        res = []
        for inst in instruments:
            try:
                tradingsymbol = inst.get("tradingsymbol", "")
                instrument_type = inst.get("instrument_type", "")
                name = inst.get("name", "")  # underlying name
                if underlying.upper() in tradingsymbol and instrument_type in ("CE", "PE"):
                    if expiry and expiry not in tradingsymbol:
                        continue
                    res.append(inst)
            except Exception:
                continue
        return res

    def fetch_quotes(self, tradingsymbols: List[str]):
        """
        Fetch quote/LTP for a list of tradingsymbols using kite.ltp
        tradingsymbols e.g. ['NSE:RELIANCE21SEP4200CE', ...]
        """
        if not self.kite:
            logger.info("PAPER: Would fetch quotes for: %s", tradingsymbols)
            return {}
        q = self.kite.ltp(tradingsymbols)
        return q

    def place_order(self, tradingsymbol: str, side: str = "BUY", qty: int = 1, product="MIS", order_type="MARKET"):
        """
        Place a simple market order. VERY basic — expand for qty calculation, slippage, error handling.
        """
        if not self.kite:
            logger.info("PAPER: Would place order %s %s qty=%s", side, tradingsymbol, qty)
            return {"paper": True, "action": side, "tradingsymbol": tradingsymbol, "qty": qty}
        try:
            res = self.kite.place_order(
                tradingsymbol=tradingsymbol,
                exchange="NSE",
                transaction_type="BUY" if side.upper()=="BUY" else "SELL",
                quantity=qty,
                order_type=order_type,
                product=product
            )
            return res
        except Exception as e:
            logger.exception("Order failed")
            return {"error": str(e)}

# ---------------- Example usage ----------------
if __name__ == "__main__":
    # Make sure to export KITE_API_KEY and KITE_ACCESS_TOKEN in env for live usage
    kh = KiteHelper()
    if kh.kite:
        instruments = kh.load_instruments()
        print("Total instruments:", len(instruments))
        chain = kh.filter_option_chain(instruments, underlying="RELIANCE")
        print("Found option instruments:", len(chain))
        # pick first 5 tradingsymbols to fetch quotes
        syms = [i["tradingsymbol"] for i in chain[:5]]
        print(kh.fetch_quotes(["NSE:" + s for s in syms]))
    else:
        print("Running in PAPER mode. No kite credentials found.")
        print("Example: kh.place_order('RELIANCE', 'BUY', qty=1)")
