CREATE TABLE IF NOT EXISTS public.coin
(
    id text COLLATE pg_catalog."default" NOT NULL,
    symbol text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    market_cap bigint NOT NULL,
    ticker text COLLATE pg_catalog."default" NOT NULL,
    enabled boolean DEFAULT false,
    CONSTRAINT coin_pkey PRIMARY KEY (id)
);