import os
import pathlib

import psycopg2

BASE_DIR = pathlib.Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "SeedData.sql"

def get_connection_params():
    return {
        "dbname": os.getenv("DB_NAME", "basketball"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "secret"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }

def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"Impossible de trouver {SQL_FILE}")

    params = get_connection_params()
    print(f"Connexion a {params['dbname']}@{params['host']}:{params['port']} ...")

    sql_script = SQL_FILE.read_text(encoding="utf-8-sig")

    with psycopg2.connect(**params) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql_script)
            print("Base remplie avec SeedData.sql")

if __name__ == "__main__":
    main()
