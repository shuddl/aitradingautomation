import asyncio, datetime as dt, logging, aiohttp, os, time
from typing import List, Dict, Any
from .SchwabConnector import SchwabConnector
import websockets, json, redis

REDIS_STREAM = "ticks"

class DataFetcher:
    def __init__(self, schwab: SchwabConnector, polygon_key: str):
        # ...existing code...
        self.schwab = schwab
        self.polygon_key = polygon_key

    async def polygon_bars(self, symbol: str, start: dt.datetime, end: dt.datetime, timespan="second") -> List[Dict]:
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{timespan}/{start.isoformat()}/{end.isoformat()}?apiKey={self.polygon_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("results", [])

    async def realtime_stream(self, symbols: List[str]):
        """
        Consumes Polygon websocket, serialises quotes to Redis Stream.
        """
        api_key = self.polygon_key
        uri = f"wss://socket.polygon.io/stocks?apiKey={api_key}"
        rdb = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)

        async with websockets.connect(uri, ping_interval=30) as ws:
            await ws.send(json.dumps({"action": "subscribe", "params": ",".join(f"T.{s}" for s in symbols)}))
            logging.info("Subscribed to Polygon stream.")
            while True:
                msg = await ws.recv()
                rdb.xadd(REDIS_STREAM, {"data": msg, "ts": int(time.time()*1000)})