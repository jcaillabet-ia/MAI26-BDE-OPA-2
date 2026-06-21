import time
import sys

import coingecko as cg
import database as db

def main():
    try:
        conn = db.open_connection()
        with conn.cursor() as cursor:
            #
            # Liste des monnaies    
            #
            coins = cg.list_coins()
            coin_data = [(c["id"], c["symbol"], c["name"]) for c in coins]
            insert_query = """
                INSERT INTO coin (id, symbol, name, market_cap)
                VALUES (%s, %s, %s, 0)
                ON CONFLICT (id) DO NOTHING;
            """
            cursor.executemany(insert_query, coin_data)

            # 
            # Récupération de l'information market_cap
            # 
            markets = cg.list_markets()
            update_data = []
            for m in markets:
                m_cap = m.get("market_cap")
                m_cap_val = int(m_cap) if m_cap is not None else 0
                update_data.append((m_cap_val, m["id"]))
            update_query = """
                UPDATE coin
                SET market_cap = %s
                WHERE id = %s;
            """
            cursor.executemany(update_query, update_data)

            #
            # Liste des tickers pour les 250 coins
            #
            for index, crypto in enumerate(markets, 1):
                crypto_id = crypto["id"]

                tickers = cg.list_tickers(crypto_id)

                if tickers and "tickers" in tickers:
                    tickers_list = tickers["tickers"]

                    query_parts = []
                    all_params = []

                    for t in tickers_list:
                        base = t.get("base")
                        target = t.get("target")

                        if not base or not target:
                            continue

                        market_info = t.get("market", {})
                        market_id = market_info.get("identifier", "unknown")
                        ticker_id = f"{market_id}_{base}_{target}".lower()
                        market_name = market_info.get("name", "Unknown")

                        query_parts.append("""
                            INSERT INTO ticker (id, name, base, target)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING;
                        """)
                        all_params.extend([ticker_id, market_name, base, target])

                        query_parts.append("""
                            INSERT INTO coin_ticker (coin_id, ticker_id)
                            VALUES (%s, %s)
                            ON CONFLICT (coin_id, ticker_id) DO NOTHING;
                        """)
                        all_params.extend([crypto_id, ticker_id])

                    if query_parts:
                        query = "".join(query_parts)
                        cursor.execute(query, all_params)

                print(crypto_id)   

        conn.commit()
    except Exception as e:
        print(f"[ERREUR]: {e}", file=sys.stderr)
        conn.rollback()

    conn.close()
    print("\n[FIN] Script terminé avec succès.")

if __name__ == "__main__":
    main()
