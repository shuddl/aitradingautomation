```mermaid
flowchart LR
    A[API‑Connector] -->|ticks & orders| B(Data‑Pipeline)
    B --> C(Strategy‑Engine)
    C --> D(AI‑Engine)
    D --> E(Risk‑Manager)
    E --> F(Execution‑Engine)
    B --> G(Backtester)
    A --> G
    B --> H(Dashboard)
```
Data‑flow: real‑time tick → Strategy‑Engine → AI decision → Risk check → Execution.

Security & Compliance
– OAuth2 stored in Secrets Mgr  
– Signed orders, TLS 1.2+, IAM roles per task, FINRA OATS ready logs.
