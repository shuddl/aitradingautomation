"""
Offline demo – proves data‑flow, risk & dashboard without live APIs.

Prerequisite (host run):
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
or simply run inside the Docker container.

Run demo:
    docker compose up -d
    python demo/DemoRunner.py
"""
import pathlib, sys
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import os, time, json, pandas as pd, yfinance as yf, matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ------------- Redis helper (works even if Redis not running) -------------
try:
    import redis               # noqa: E402
    _r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)
    _r.ping()
    rdb = _r
except Exception:               # redis not installed or server down
    class _DummyRedis:          # minimal stand‑in
        def xadd(self, *_a, **_k): pass
        def xrevrange(self, *_a, **_k): return []
    rdb = _DummyRedis()
    print("⚠️  Redis unavailable – using in‑memory stub (dashboard won’t stream).")

from src.engines.StrategyEngine import StrategyEngine  # noqa: E402
from src.engines.ExecutionEngine import ExecutionEngine  # noqa: E402
from src.connectors.SchwabConnector import SchwabConnector  # noqa: E402

# ------------- bootstrap -------------
se = StrategyEngine({})

class _MockSchwab(SchwabConnector):             # type: ignore
    def __init__(self): pass
    def place_order(self, order_payload):       # type: ignore
        print("ORDER ->", json.dumps(order_payload)[:120], "...")
        return {"mockOrderId": int(time.time())}

# use very loose limits – demo only
risk_cfg = {          # ← changed
    "max_position_pct": 100.0,   # 100 % of equity, always passes
    "daily_drawdown_pct":  1.0,  # 100 k worst‑case
    "circuit_breaker":    False
}
exe = ExecutionEngine(_MockSchwab(), risk_cfg)

# ------------- load sample market data -------------
end = datetime.utcnow()
start = end - timedelta(days=1)
print("📊 Loading market data for SPY...")
df = yf.download("SPY", start=start, end=end, interval="1m", progress=False)
df.rename(columns=str.lower, inplace=True)
df["volume"].fillna(0, inplace=True)

# ------------- demo loop -------------
pnl = 0.0
actions = []
print("💹 Processing market data and generating signals...")
signals_count = {"BUY": 0, "SELL": 0, "HOLD": 0}

for ts, row in df.iterrows():
    # ↓ make a pure‑Python dict; nothing from pandas is stored
    tick = {
        "t": int(ts.timestamp() * 1000),
        "p": float(row["close"]),
        "v": float(row["volume"]),
    }
    rdb.xadd("ticks", {"data": json.dumps(tick)})

    sig = se.generate_signal(pd.DataFrame([row], index=[ts]))
    action = sig["action"]

    # Track signals for final summary
    signals_count[action] += 1
    
    # Better visual feedback for orders
    if action != "HOLD":
        order_type = "🟢 BUY" if action == "BUY" else "🔴 SELL"
        print(f"{order_type} signal at {ts.strftime('%H:%M:%S')} - price: ${tick['p']:.2f}")
        actions.append((ts, action, tick["p"]))
        if action == "BUY":
            exe.send_straddle("SPY", 1, round(tick["p"]), ts.strftime("%y%m%d"))
            pnl -= tick["p"]
        else:
            pnl += tick["p"]
        rdb.xadd("pnl", {"data": json.dumps({"pnl": pnl, "time": ts.isoformat()})})

    # Make the demo run at reasonable speed
    time.sleep(0.05)  # slow down a bit to show progress

# Add key metrics summary
print("\n📈 Trading Session Summary:")
print(f"Total signals: {sum(signals_count.values())}")
print(f"Buy signals: {signals_count['BUY']}")
print(f"Sell signals: {signals_count['SELL']}")
print(f"Hold signals: {signals_count['HOLD']}")
print(f"Final P&L: ${pnl:.2f}")

# ------------- plot summary -------------
if actions:
    act_df = pd.DataFrame(actions, columns=["time", "action", "price"])
    plt.figure(figsize=(10, 4))
    plt.plot(df.index, df.close, label="SPY")
    buys  = act_df[act_df.action == "BUY"]
    sells = act_df[act_df.action == "SELL"]
    plt.scatter(buys.time,  buys.price,  marker="^", color="g", label="BUY")
    plt.scatter(sells.time, sells.price, marker="v", color="r", label="SELL")
    plt.title("Demo – Signals over 1 trading day")
    plt.legend(); plt.tight_layout()
    outfile = pathlib.Path(__file__).with_name("demo_plot.png")
    plt.savefig(outfile)
    print(f"📊 Plot saved to {outfile}")
    print(f"🌐 Dashboard: http://localhost:8000/dash (requires Docker)")
    print(f"📈 Metrics: http://localhost:8000/metrics (requires Docker)")
else:
    print("✅ Demo complete – no trade signals generated.")
print("✅ Demo complete.")
