import os
import sys
import database as db

def main():
    try:
        conn = db.open_connection()
        cursor = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as schema_file:
            schema_sql = schema_file.read()

        cursor.execute(schema_sql)
        conn.commit()
        
        print("\n[SUCCÈS] Schéma chargé avec succès !")
        
        cursor.close()
        conn.close()
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ERREUR] Échec : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
