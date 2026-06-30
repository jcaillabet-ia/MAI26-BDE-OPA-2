import ccxt.pro as ccxtpro
import asyncio

async def main():
    exchange = ccxtpro.binance({'newUpdates': False})
    symbol = 'BTC/USDT'
    timeframe = '1m'
    limit = 1000
    since = None
    params = {}
    while True:
        try:
            candles = await exchange.watch_ohlcv(symbol, timeframe, since, limit, params)
            print(exchange.iso8601(exchange.milliseconds()), candles)
        except Exception as e:
            print(e)
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
