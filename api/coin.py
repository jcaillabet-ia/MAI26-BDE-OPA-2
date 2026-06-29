from dotenv import load_dotenv
import ccxt
import os
import time

load_dotenv(override=True)
base_url = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")

def get_exchange(symbol):
    if symbol in ["BTC/USDT"]:
        return ccxt.binance()

def fetch_coin(symbol = 'BTC/USDT', limit = 1000):
    exchange = get_exchange(symbol)
    timeframe = '1m'
    timeframe_ms = 60 * 1000

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
