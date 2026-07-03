CREATE KEYSPACE IF NOT EXISTS crypto_bot 
WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1}};

CREATE TABLE IF NOT EXISTS crypto_bot.candles (
    crypto_id text,
    bucket_date date,
    timestamp timestamp,
    open decimal,
    high decimal,
    low decimal,
    close decimal,
    volume decimal,
    PRIMARY KEY ((crypto_id, bucket_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);