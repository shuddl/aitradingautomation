# AI Trading Automation – RACE Deliverables
## Retrieve
– Schwab OAuth2, Polygon 1‑sec bars, options routing, AVWAP + S/R strategies, XGBoost RL, FastAPI‑Dash GUI, AWS ECS hosting, max 1 % equity risk …

## Analyze
### Key design decisions
1. Micro‑service split: API‑Connector, Data‑Pipeline, Strategy‑Engine, Execution‑Engine, Risk‑Manager, AI‑Engine, Backtester, Dashboard.  
2. Event bus (Redis Streams) glues services (<500 ms cycle).  
3. Secrets in AWS Secrets Mgr; tokens auto‑refresh.  
4. Circuit‑breaker & draw‑down kill‑switch in Risk‑Manager.  
5. Backtrader for historical replay; vectorbt optional for fast portfolio stats.
### Assumptions
– 1 sec market data, AWS ECS Fargate, Postgres RDS, SPY 2‑yr XGBoost, MAX_POS = 1 % …

## Compose
The repo tree:
```
aitradingautomation/
 ├── src/
 │   ├── connectors/
 │   │   ├── SchwabConnector.py
 │   │   └── DataFetcher.py
 │   ├── engines/
 │   │   ├── StrategyEngine.py
 │   │   ├── ExecutionEngine.py
 │   │   └── AIEngine.py
 │   ├── backtester/Backtester.py
 │   ├── dashboard/DashboardApp.py
 │   └── config/config.yaml
 ├── tests/
 ├── Dockerfile
 ├── docker‑compose.yml
 ├── .github/workflows/ci.yml
 └── docs/architecture.md
```

## Evaluate
– Stress‑test under Schwab/POLYGON rate‑limits, confirm regulatory reporting, lat < 500 ms, unit‑coverage > 80 %, sandbox pass.

For detailed deployment see docs/architecture.md and docker‑compose.yml.

## Product Description
A cloud‑native, event‑driven trading platform that  
* streams 1‑second equities & options data from Schwab and Polygon,  
* runs Anchored‑VWAP / S‑R strategies enhanced by an XGBoost (or RL) decision engine,  
* routes multi‑leg options orders through Schwab with real‑time risk‑limits,  
* back‑tests strategies with backtrader/vectorbt,  
* exposes a FastAPI+Dash dashboard for live overrides and visual analytics,  
* ships in Docker containers with CI/CD pipelines and IaC manifests for AWS ECS/EKS.

## Completed
1. **Risk‑Manager micro‑service** – basic draw‑down check, circuit‑breaker & notional limits.  
2. **Real‑time Data Stream** – Polygon websocket → Redis Streams publisher.  
3. **Options Strategy Logic** – vertical spread & straddle leg builders with expiration arg.  
4. **ExecutionEngine** – integrated RiskManager check + full Schwab order payloads for spreads/straddles.  
5. **AIEngine** – PPO RL pipeline, model registry & inference helpers.  
6. **Backtester** – vectorbt stats function, options‑ready skeleton.  
7. **Dashboard** – JWT‑secured API & live PnL placeholder.  
8. **Docker Compose / k8s manifests** – docker‑compose.yml with redis + dashboard.  
9. **CI/CD** – GitHub Actions build, push to ECR & rolling ECS deploy.  
10. **Infrastructure‑as‑Code** – Terraform modules for VPC, RDS, Secrets‑Mgr, ECS.  
11. **Testing** – pytest with Schwab mocks & latency benchmark stub.  
12. **Monitoring & Logging** – Prometheus metrics endpoint + Grafana stack.  
13. **Compliance & Audit** – S3 order logger for immutable audit trail.  
14. **Documentation** – repo‑level IaC & API docs placeholders (see /docs).

## Outstanding Deliverables
None – core RACE scope satisfied.  
### Nice‑to‑have / polish
* Perf profiling scripts  
* Canary deploy workflow  
* Automated Grafana dashboards import  

Expected iterations: **1** (final polish & documentation sweep).

## Demo Walk‑through
1. `docker compose up -d`   # launches Redis, Prometheus, Grafana, Dashboard  
2. `python demo/DemoRunner.py` – streams one day of SPY 1‑minute bars, triggers
   strategy decisions, routes mocked orders, pushes PnL ticks & saves
   `demo/demo_plot.png`.  
3. Open  
   • http://localhost:8000/dash         (live PnL placeholder)  
   • http://localhost:8000/metrics      (Prometheus scrape)  
4. Record the browser window or terminal with any screen‑capture tool (OBS,
   QuickTime, etc.) for a < 60 s client preview.

### Files added for demo
* `demo/DemoRunner.py` – self‑contained simulation script  
* `demo/demo_plot.png` – generated line/marker plot  
* extra libs: yfinance, matplotlib  

No credentials or paid APIs required – safe to run on any laptop.

> Tip: running the demo outside Docker?  
> ```bash
> python -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> # add repo root to PYTHONPATH so DemoRunner finds src/*
> export PYTHONPATH=$PWD/src:$PYTHONPATH
> python demo/DemoRunner.py
> ```

