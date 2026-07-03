from dotenv import load_dotenv
import httpx
import os
import time
import ccxt

from coingecko_sdk import Coingecko

from multiprocessing import Pool

load_dotenv(override=True)
base_url = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

client = Coingecko(
    demo_api_key=COINGECKO_API_KEY,
    environment="demo",
)

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

def get_markets_length(name): 
    try:
        exchange = getattr(ccxt, name)()
        markets = list(exchange.load_markets().values())
        return {
            'name': name,
            'nb': len(markets),
            'markets': [x['base'] for x in markets]
        }
    except Exception as e:
        return {
            'name': name,
            'nb': 0,
            'markets': []
        }

def build_dict(length=250):
    # Liste des exchanges
    exchange_names = ccxt.exchanges
    with Pool() as p:
        exchanges = p.map(get_markets_length, exchange_names)
    exchanges.sort(key=lambda x: x['nb'], reverse=True)

    # Liste des monaies
    coin_markets = client.coins.markets.get(
        vs_currency='eur',
        per_page=length,
        page=1
    )

    # Construction du dictionnaire
    coins = []
    for coin_market in coin_markets:
        print(coin_market.symbol)
        for exchange in exchanges:
            if coin_market.symbol.upper() in exchange['markets']:
                coins.append({
                    'symbol': coin_market.symbol,
                    'exchange': exchange['name']
                })
                break
    print(coins)
    return coins

