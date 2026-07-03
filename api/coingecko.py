from dotenv import load_dotenv
import httpx
import os
import time
import ccxt

from pathlib import Path

import json

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
            'markets': [{'base': x['base'], 'quote': x['quote']}  for x in markets]
        }
    except Exception as e:
        return {
            'name': name,
            'nb': 0,
            'markets': []
        }

def build_dict(length=250):
    if Path('./exchanges.json').exists():
        with open('./exchanges.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    # Liste des exchanges
    exchange_names = ccxt.exchanges
    with Pool() as p:
        exchanges = p.map(get_markets_length, exchange_names)
    exchanges.sort(key=lambda x: x['nb'], reverse=True)
    # on privilégie binance
    exchanges = exchanges[2:]

    # Liste des monaies
    coin_markets = client.coins.markets.get(
        vs_currency='eur',
        per_page=length,
        page=1
    )

    # Construction du dictionnaire
    coins = []
    for coin_market in coin_markets:
        _break = False
        for exchange in exchanges:
            for market in exchange['markets']:
                if coin_market.symbol.upper() in market['base']:
                    coins.append({
                        'id': coin_market.id,
                        'name': coin_market.name,
                        'symbol': market['base'] + '/' + market['quote'],
                        'market_cap': coin_market.market_cap,
                        'exchange': exchange['name']
                    })
                    _break = True
                    break
            if _break:
                break

    with open('exchanges.json', 'w', encoding='utf-8') as f:
        json.dump(coins, f, ensure_ascii=False, indent=4)

    return coins

