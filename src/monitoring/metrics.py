from prometheus_client import Counter, Histogram

# counters
ORDERS_TOTAL = Counter("orders_total", "Total routed orders", ["symbol", "side"])
ERRORS_TOTAL = Counter("errors_total", "Total errors", ["module"])

# latency
DECISION_LATENCY = Histogram("decision_latency_ms", "End‑to‑end decision latency (ms)")
