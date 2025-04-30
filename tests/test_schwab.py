import requests_mock, os
from src.connectors.SchwabConnector import SchwabConnector

def test_get_quote():
    sc = SchwabConnector("id", "uri", "acct")
    with requests_mock.Mocker() as m:
        m.get("https://api.schwabapi.com/v1/marketdata/SPY/quotes", json={"lastPrice": 1})
        sc.token = {"access_token": "x", "expires_at": 9e9}  # bypass auth
        quote = sc.get_quote("SPY")
        assert quote["lastPrice"] == 1
