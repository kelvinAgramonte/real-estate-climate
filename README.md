# Real Estate Listings + Climate Data Exercise

![CI](https://github.com/kelvinAgramonte/real-estate-climate/actions/workflows/ci.yml/badge.svg)

- 📘 **Architecture**: see [docs/architecture.md](docs/architecture.md)

## Overview

This short coding exercise is designed to assess your ability to:

- Work with real-world style CSV data
- Normalize and validate inputs
- Deduplicate, filter, and join datasets
- Produce clean, structured JSON output
- Communicate your design and reasoning

You should be able to complete the exercise in **~15–20 minutes**.  
The goal is not to write a perfect production system, but to see how you approach a realistic data-transformation task and explain your choices.

## Requirements
You are allowed to use whatever language you work best in such as python, javascript, go, etc. You may also use any library you'd like to such as pandas or other libraries. 

When you are done, please create a new github repo and push your solution to the repo, and share with your interviewer.

---

## Task

You are given two CSV files:

- **`/data/listings.csv`** — contains real estate property listings  
  (fields include: `apn`, `address`, `city`, `state`, `zip`, `price`, `beds`, `baths`, `sqft`, `status`)
- **`/data/climate.csv`** — contains climate info keyed by APN  
  (fields include: `apn`, `flood_zone`, `avg_rain_inches`)

Your job is to write a script that:

1. **Normalizes APNs**

   - `listings.csv` uses APNs with dashes, `climate.csv` uses digits only.
   - Normalize both by stripping all non-digit characters.

2. **Filters listings**

   - Keep only rows where `status` is one of: `for_sale`, `pending`, `sold`.
   - Discard rows missing essential fields (`apn`, `address`, `zip`, `price`, `sqft`).

3. **Deduplicates by APN**

   - If multiple listings share the same normalized APN, keep the one with the **lowest price**.

4. **Enriches with climate data**

   - Join on normalized APN.
   - If no match exists, set `flood_zone` and `avg_rain_inches` to `null`.

5. **Adds derived fields**

   - Compute `price_per_sqft = round(price / sqft)`.
   - Add `full_address = "{address}, {city}, {state} {zip}"`.

6. **Sorts output**

   - Sort by `price` (lowest→highest).

7. **Outputs JSON**
   - Save results to `listings_enriched.json`.
   - Each object should include:

```json
{
  "apn": "123-456-789",
  "full_address": "123 Main St, Miami, FL 33101",
  "price": 250000,
  "beds": 3,
  "baths": 2,
  "sqft": 1600,
  "price_per_sqft": 156,
  "status": "for_sale",
  "flood_zone": "AE",
  "avg_rain_inches": 54.2
}
```
"# real-estate-climate" 
