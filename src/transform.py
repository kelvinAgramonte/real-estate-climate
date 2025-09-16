from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from .utils import normalize_apn, ALLOWED_STATUSES

def load_csv(path: Path) -> pd.DataFrame:
    # Keep strings; we’ll coerce numerics ourselves
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        na_values=["", "na", "NA", "null", "None"],
    )

def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def transform(listings: pd.DataFrame, climate: pd.DataFrame) -> pd.DataFrame:
    listings = listings.copy()
    climate = climate.copy()

    # 1) Normalize APNs
    listings["apn_norm"] = listings["apn"].map(normalize_apn)
    climate["apn_norm"] = climate["apn"].map(normalize_apn)

    # 2) Filter listings
    listings["status"] = listings["status"].str.strip().str.lower()
    listings = listings[listings["status"].isin(ALLOWED_STATUSES)].copy()

    listings["price_num"] = coerce_numeric(listings["price"])
    listings["sqft_num"]  = coerce_numeric(listings["sqft"])

    mask = (
        listings["apn_norm"].notna()
        & listings["address"].astype(str).str.len().gt(0)
        & listings["zip"].astype(str).str.len().gt(0)
        & listings["price_num"].notna()
        & listings["sqft_num"].notna()
        & (listings["sqft_num"] > 0)
    )
    listings = listings[mask].copy()

    # 3) Deduplicate by APN (keep lowest price)
    listings.sort_values(["apn_norm", "price_num"], ascending=[True, True], inplace=True)
    listings = listings.drop_duplicates(subset=["apn_norm"], keep="first")

    # 4) Enrich with climate
    climate = climate[["apn_norm", "flood_zone", "avg_rain_inches"]].copy()
    climate["avg_rain_inches"] = coerce_numeric(climate["avg_rain_inches"])
    merged = listings.merge(climate, on="apn_norm", how="left")

    # 5) Derived fields
    merged["price_per_sqft"] = (merged["price_num"] / merged["sqft_num"]).round().astype("Int64")
    merged["full_address"] = merged.apply(
        lambda r: f"{r['address']}, {r.get('city','')}, {r.get('state','')} {r['zip']}".replace(" ,", "").strip(),
        axis=1,
    )

    # 6) Output + sort
    out = merged[[
        "apn_norm", "full_address", "price_num", "beds", "baths", "sqft_num",
        "price_per_sqft", "status", "flood_zone", "avg_rain_inches"
    ]].rename(columns={
        "apn_norm": "apn",
        "price_num": "price",
        "sqft_num": "sqft",
    })

    for col in ["price", "beds", "baths", "sqft", "price_per_sqft"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.sort_values("price", ascending=True, kind="mergesort").reset_index(drop=True)
    return out

def to_json(df: pd.DataFrame, path: Path) -> None:
    import json
    records = []
    for _, r in df.iterrows():
        obj = {
            "apn": str(r["apn"]) if pd.notna(r["apn"]) else None,
            "full_address": r["full_address"] if pd.notna(r["full_address"]) else None,
            "price": int(r["price"]) if pd.notna(r["price"]) else None,
            "beds": int(r["beds"]) if pd.notna(r["beds"]) else None,
            "baths": int(r["baths"]) if pd.notna(r["baths"]) else None,
            "sqft": int(r["sqft"]) if pd.notna(r["sqft"]) else None,
            "price_per_sqft": int(r["price_per_sqft"]) if pd.notna(r["price_per_sqft"]) else None,
            "status": r["status"] if pd.notna(r["status"]) else None,
            "flood_zone": r["flood_zone"] if pd.notna(r["flood_zone"]) else None,
            "avg_rain_inches": float(r["avg_rain_inches"]) if pd.notna(r["avg_rain_inches"]) else None,
        }
        records.append(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--listings", type=Path, required=True)
    p.add_argument("--climate",  type=Path, required=True)
    p.add_argument("--out",      type=Path, default=Path("data/listings_enriched.json"))
    args = p.parse_args()

    listings = load_csv(args.listings)
    climate  = load_csv(args.climate)
    df = transform(listings, climate)
    to_json(df, args.out)
    print(f"Wrote {args.out} with {len(df)} records.")

if __name__ == "__main__":
    main()
