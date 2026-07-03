FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "cryptobot.ingestion.fetch_ohlcv", "--asset", "BTC", "--timeframe", "1h", "--n-points", "100", "--output", "data/samples/btc_ohlcv_sample.json"]
