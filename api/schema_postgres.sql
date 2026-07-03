CREATE TABLE IF NOT EXISTS public.coin
(
    id text COLLATE pg_catalog."default" NOT NULL,
    symbol text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    market_cap bigint NOT NULL,
    enabled boolean DEFAULT false,
    CONSTRAINT coin_pkey PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.coin ALTER COLUMN market_cap TYPE bigint;

ALTER TABLE IF EXISTS public.coin
    OWNER to postgres;

CREATE TABLE IF NOT EXISTS public.ticker
(
    id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    base text COLLATE pg_catalog."default" NOT NULL,
    target text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT ticker_pkey PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.ticker
    OWNER to postgres;

CREATE TABLE IF NOT EXISTS public.coin_ticker
(
    coin_id text COLLATE pg_catalog."default" NOT NULL,
    ticker_id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT coin_ticker_pkey PRIMARY KEY (coin_id, ticker_id),
    CONSTRAINT coin_id_fk FOREIGN KEY (coin_id)
        REFERENCES public.coin (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT ticker_id_fk FOREIGN KEY (ticker_id)
        REFERENCES public.ticker (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.coin_ticker
    OWNER to postgres;