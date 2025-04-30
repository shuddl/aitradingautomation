import time, logging
from typing import Dict, Any

class RiskManager:
    """
    Centralised risk controls: max‑position %, day draw‑down %, circuit‑breaker.
    Keeps an in‑memory snapshot; plug real DB/clearing API for prod.
    """
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.reset_day()

    # ---------- intraday state ----------
    def reset_day(self):
        self.day_start_equity = self._get_account_equity()
        self.day_killed = False
        logging.info("RiskManager day reset.")

    def _get_account_equity(self) -> float:
        # TODO: pull from broker; stubbed for now
        return 100_000.0

    def _current_pnl(self) -> float:
        # TODO: pull unrealised PnL; stubbed
        return 0.0

    # ---------- checks ----------
    def check_drawdown(self):
        dd = -(self._current_pnl()) / self.day_start_equity
        if dd >= self.cfg["daily_drawdown_pct"]:
            self.day_killed = True
            logging.error("Daily draw‑down breached, trading halted!")

    def allow_trade(self, notional: float) -> bool:
        if self.day_killed and self.cfg["circuit_breaker"]:
            return False
        self.check_drawdown()
        return notional <= self.cfg["max_position_pct"] * self._get_account_equity()
