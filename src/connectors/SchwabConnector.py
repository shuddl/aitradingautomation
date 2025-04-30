import os, time, requests, logging, json
from typing import Dict, Any

class SchwabConnector:
    BASE_URL = "https://api.schwabapi.com/v1"

    def __init__(self, client_id: str, redirect_uri: str, account_id: str, token_path: str = "./.schwab_token.json"):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.account_id = account_id
        self.token_path = token_path
        self._load_token()

    # ---------- OAuth2 ----------
    def _load_token(self):
        if os.path.exists(self.token_path):
            self.token = json.load(open(self.token_path))
        else:
            self.token = {}

    def _refresh_token(self):
        if self.token.get("expires_at", 0) - time.time() > 120:
            return
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.token["refresh_token"],
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        r = requests.post(f"{self.BASE_URL}/oauth2/token", data=payload, timeout=30)
        r.raise_for_status()
        self.token = r.json()
        self.token["expires_at"] = time.time() + self.token["expires_in"]
        json.dump(self.token, open(self.token_path, "w"))
        logging.info("Schwab token refreshed.")

    def _headers(self) -> Dict[str, str]:
        self._refresh_token()
        return {"Authorization": f"Bearer {self.token['access_token']}", "Content-Type": "application/json"}

    # ---------- Market Data ----------
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        r = requests.get(f"{self.BASE_URL}/marketdata/{symbol}/quotes", headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.json()

    # ---------- Order Routing ----------
    def place_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/accounts/{self.account_id}/orders"
        r = requests.post(url, headers=self._headers(), json=order_payload, timeout=10)
        r.raise_for_status()
        return r.json()