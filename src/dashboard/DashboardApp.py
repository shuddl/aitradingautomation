from fastapi import FastAPI, Depends, HTTPException, status, Response
from jose import jwt, JWTError
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import os, redis, json
import dash, dash_html_components as html

SECRET = os.getenv("JWT_SECRET", "dev")

def _auth(token: str = ""):
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

app = FastAPI(title="AI Trading Automation Dashboard")

@app.get("/live_pnl", dependencies=[Depends(_auth)])
def live_pnl():
    """Return latest PnL from Redis Stream (stub)."""
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)
    last = r.xrevrange("pnl", count=1)
    return json.loads(last[0][1]["data"]) if last else {"pnl": 0}

# Dash override panel
dash_app = dash.Dash(__name__, server=app)     # attach to FastAPI
dash_app.layout = html.Div([
    html.H1("Live PnL"),
    html.Div(id="pnl"),
])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
