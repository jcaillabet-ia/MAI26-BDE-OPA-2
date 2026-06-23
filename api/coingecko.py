from dotenv import load_dotenv
import httpx
import os
import time

load_dotenv(override=True)
base_url = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

def list_coins():
    with httpx.Client(base_url=base_url, timeout=10.0) as coingecko_client:
        time.sleep(0.6)
        response = coingecko_client.get(f"/coins/list?x_cg_demo_api_key={COINGECKO_API_KEY}")
        response.raise_for_status()
        return response.json()

def list_markets():
    with httpx.Client(base_url=base_url, timeout=10.0) as coingecko_client:
        time.sleep(0.6)
        response = coingecko_client.get(f"/coins/markets?vs_currency=eur&per_page=250&page=1&x_cg_demo_api_key={COINGECKO_API_KEY}")
        response.raise_for_status()
        return response.json()

def list_tickers(coin_id):
    with httpx.Client(base_url=base_url, timeout=10.0) as coingecko_client:
        time.sleep(0.6)
        response = coingecko_client.get(f"/coins/{coin_id}/tickers?x_cg_demo_api_key={COINGECKO_API_KEY}")
        response.raise_for_status()
        return response.json()
    