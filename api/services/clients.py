import ccxt
from ccxt.base.errors import BadSymbol
from coingecko_sdk import Coingecko
from dotenv import load_dotenv
import json
from pathlib import Path
from multiprocessing import Pool
import os


def get_markets_length(name): 
    try:
        exchange = getattr(ccxt, name)()
        markets = list(exchange.load_markets().values())
        return {
            'ref': exchange,
            'name': name,
            'nb': len(markets),
            'markets': [{'base': x['base'], 'quote': x['quote']}  for x in markets]
        }
    except Exception as e:
        return {
            'ref': None,
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
    exchanges = exchanges[1:]
    exchanges = list(filter(lambda x: x['nb'] > 0, exchanges))

    load_dotenv(override=True)
    COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

    client = Coingecko(
        demo_api_key=COINGECKO_API_KEY,
        environment="demo",
    )

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
                if coin_market.symbol.upper() == market['base'].upper():

                    symbol = market['base'] + '/' + market['quote']
                    try:
                        market_data = exchange['ref'].market(symbol)
                    except BadSymbol:
                        continue

                    if not market_data['active']:
                        continue

                    info = None
                    if 'info' in market_data:
                        info = market_data['info']

                    if info and 'enableDisplay' in info and not info['enableDisplay']:
                        continue

                    coins.append({
                        'id': coin_market.id,
                        'name': coin_market.name,
                        'base': market['base'],
                        'quote': market['quote'],
                        'symbol': symbol,
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