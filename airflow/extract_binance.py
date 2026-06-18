import ccxt
from datetime import datetime

def main():
    exchange = ccxt.binance()

    # Configuration
    symbol = 'BTC/USDT'
    timeframe = '1h'  # Options: '1m', '5m', '1h', '1d', etc.
    limit = 5         # Nombre de bougies à récupérer

    try:
        # Récupération de l'historique
        candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        print(f"--- Historique des {limit} dernières bougies ({timeframe}) ---")
        for candle in candles:
            # Structure d'une bougie renvoyée par CCXT :
            # [Timestamp_MS, Open, High, Low, Close, Volume]
            
            # Convertit le timestamp en millisecondes en objet datetime lisible
            date = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"Date: {date} | Ouv: {candle[1]}$ | Haut: {candle[2]}$ | Bas: {candle[3]}$ | Clôt: {candle[4]}$ | Vol: {candle[5]}")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

    try:
        # Récupération du snapshot temps réel
        ticker = exchange.fetch_ticker(symbol)

        ts_ms = ticker['timestamp']  # Exemple: 1781701726123
        dt_string = ticker['datetime']  # Exemple: '2026-06-17T13:08:46.123Z'
        
        # 2. Si tu veux reformater le timestamp à ta sauce locale :
        date_locale = datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        print(f"--- Cours en Temps Réel pour {symbol} ---")
        print(f"Horodatage Échange (ISO) : {dt_string}")
        print(f"Horodatage Local         : {date_locale}")
        print(f"Dernier prix (Last Price) : {ticker['last']} USDT")
        print(f"Plus haut 24h (High)       : {ticker['high']} USDT")
        print(f"Plus bas 24h (Low)         : {ticker['low']} USDT")
        print(f"Volume 24h                 : {ticker['baseVolume']} BTC")
        print(f"Variation 24h              : {ticker['percentage']}%")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()
