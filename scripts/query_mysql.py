from __future__ import annotations
import argparse, os
from dotenv import load_dotenv
import mysql.connector

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sql", required=True, help="SQL to run, e.g. SELECT COUNT(*) FROM listings_enriched;")
    args = p.parse_args()

    load_dotenv()
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST","127.0.0.1"),
        user=os.getenv("MYSQL_USER","appuser"),
        password=os.getenv("MYSQL_PASSWORD","apppass"),
        database=os.getenv("MYSQL_DATABASE","realestate"),
        port=int(os.getenv("MYSQL_PORT","3307")),
    )
    cur = conn.cursor()
    cur.execute(args.sql)
    rows = cur.fetchall()
    # print headers
    headers = [d[0] for d in cur.description] if cur.description else []
    if headers:
        print("\t".join(headers))
    for r in rows:
        print("\t".join("" if v is None else str(v) for v in r))
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
