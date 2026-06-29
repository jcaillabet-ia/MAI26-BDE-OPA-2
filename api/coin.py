from dotenv import load_dotenv
import ccxt
import os

load_dotenv(override=True)
base_url = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

def fetch_coin(symbol = 'BTC/USDT', limit = 1000):
    exchange = ccxt.binance()
    timeframe = '1m'
    return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)


    