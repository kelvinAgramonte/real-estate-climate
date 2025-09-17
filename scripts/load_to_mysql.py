from __future__ import annotations
import argparse, json, os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()

    # Load env vars from .env
    load_dotenv()

    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "appuser"),
        password=os.getenv("MYSQL_PASSWORD", "apppass"),
        database=os.getenv("MYSQL_DATABASE", "realestate"),
        port=int(os.getenv("MYSQL_PORT", "3307")),
    )
    cur = conn.cursor()

    with open(args.json, "r", encoding="utf-8") as f:
        rows = json.load(f)

    sql = (
        "REPLACE INTO listings_enriched "
        "(apn, full_address, price, beds, baths, sqft, price_per_sqft, status, flood_zone, avg_rain_inches) "
        "VALUES (%(apn)s, %(full_address)s, %(price)s, %(beds)s, %(baths)s, %(sqft)s, %(price_per_sqft)s, %(status)s, %(flood_zone)s, %(avg_rain_inches)s)"
    )

    for r in rows:
        cur.execute(sql, r)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(rows)} rows into MySQL.")

if __name__ == "__main__":
    main()
