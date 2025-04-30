from typing import Dict, Any, List
from ..connectors.SchwabConnector import SchwabConnector
from .RiskManager import RiskManager

class ExecutionEngine:
    def __init__(self, schwab: SchwabConnector, risk_cfg: Dict[str, Any]):
        self.schwab = schwab
        self.risk_mgr = RiskManager(risk_cfg)

    # ---------- helpers ----------
    @staticmethod
    def _option_leg(symbol: str, qty: int, strike: float, expiry: str, right: str) -> Dict[str, Any]:
        return {
            "instrument": {
                "symbol": f"{symbol}_{expiry}_{strike}_{right}",
                "assetType": "OPTION"
            },
            "instruction": "BUY_TO_OPEN" if qty > 0 else "SELL_TO_OPEN",
            "quantity": abs(qty)
        }

    # ---------- strategies ----------
    def send_vertical_spread(self, symbol: str, qty: int, long_strike: float, short_strike: float, expiry: str):
        notional = qty * (long_strike - short_strike) * 100
        if not self.risk_mgr.allow_trade(notional):
            raise Exception("RiskManager blocked trade.")
        order = {
            "orderType": "NET_CREDIT",
            "price": "MARKET",
            "complexOrderStrategyType": "VERTICAL",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                self._option_leg(symbol,  qty, long_strike,  expiry, "C"),
                self._option_leg(symbol, -qty, short_strike, expiry, "C")
            ]
        }
        return self.schwab.place_order(order)

    def send_straddle(self, symbol: str, qty: int, strike: float, expiry: str):
        notional = qty * strike * 200  # call+put
        if not self.risk_mgr.allow_trade(notional):
            raise Exception("RiskManager blocked trade.")
        order = {
            "orderType": "NET_DEBIT",
            "price": "MARKET",
            "complexOrderStrategyType": "STRADDLE",
            "orderLegCollection": [
                self._option_leg(symbol, qty, strike, expiry, "C"),
                self._option_leg(symbol, qty, strike, expiry, "P")
            ]
        }
        return self.schwab.place_order(order)