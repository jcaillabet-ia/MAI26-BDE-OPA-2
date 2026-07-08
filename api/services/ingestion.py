from dotenv import load_dotenv
import httpx
import os
import time
import ccxt

from coingecko_sdk import Coingecko

from multiprocessing import Pool

import json
from pathlib import Path

load_dotenv(override=True)
base_url = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

client = Coingecko(
    demo_api_key=COINGECKO_API_KEY,
    environment="demo",
)

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

    #print(exchanges)
    #return {}

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

def get_exchange(dict, symbol):
    exchange_name = list(filter(lambda x: x['symbol'] == symbol, dict))[0]['exchange']
    return getattr(ccxt, exchange_name)()

def fetch_coin(dict, symbol = 'BTC/USDT', timeframe = '1m', limit = 1000):
    exchange = get_exchange(dict, symbol)
    
    timeframe_ms = 1000 * 60
    if timeframe == '1h':
        timeframe_ms = 60 * 60 * 1000
    if timeframe == '1d':
        timeframe_ms = 24 * 60 * 60 * 1000

    all_candles = []

    iterations = (limit + 999) // 1000
    since = None
    for i in range(iterations):
        candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not candles:
            break
        all_candles = candles + all_candles
        since = all_candles[0][0] - (1000 * timeframe_ms)
        time.sleep(exchange.rateLimit / 1000)

    return all_candles


