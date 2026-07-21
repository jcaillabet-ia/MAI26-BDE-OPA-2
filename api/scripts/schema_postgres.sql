CREATE TABLE IF NOT EXISTS public.coin
(
    id text COLLATE pg_catalog."default" NOT NULL,
    symbol text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    market_cap bigint NOT NULL,
    exchange text COLLATE pg_catalog."default" NOT NULL,
    enabled boolean DEFAULT false,
    score float DEFAULT -1,
    CONSTRAINT coin_pkey PRIMARY KEY (id)
);

-- CREATE TABLE IF NOT EXISTS public.candles (
--     crypto_id text,
--     bucket_date date,
--     timestamp timestamp,
--     open decimal,
--     high decimal,
--     low decimal,
--     close decimal,
--     volume decimal,
--     PRIMARY KEY (crypto_id, bucket_date, timestamp)
-- );