# live/risk_manager.py
import yaml

class RiskManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.max_risk_pct = cfg.get("risk", {}).get("max_risk_per_trade_pct", 1.0)
        self.daily_max_loss_pct = cfg.get("risk", {}).get("daily_max_loss_pct", 3.0)
        # In a real implementation you'd fetch account balances, P&L history etc.
        self.today_loss = 0.0

    def allowed_trade(self, size_pct):
        # Basic checks
        if size_pct*100 > self.max_risk_pct:
            return False
        if self.today_loss >= self.daily_max_loss_pct:
            return False
        return True

    def register_loss(self, loss_pct):
        self.today_loss += loss_pct
