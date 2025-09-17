# Real Estate Listings + Climate Data — Architecture

This document captures the **end-to-end architecture** of the ETL mini-pipeline, infra, and repository layout.

---

## 1) System Overview
md

```
flowchart LR
  A[CSV: listings.csv] -->|normalize/filter/dedup| B[Transform (Python/pandas)]
  A2[CSV: climate.csv] -->|left join on APN| B
  B -->|price_per_sqft, full_address| C[JSON: listings_enriched.json]
  C -->|loader| D[(MySQL in Docker)]
  D --> E[Ad-hoc SQL (scripts/query_mysql.py)]
  D -.-> F[Dashboards (Confluence/Jira) 🔜]
```

## 2) ETL Data Flow (pandas)
mermaid

```
flowchart TD
  L1[Load listings.csv] --> N1[Normalize APN (digits only)]
  C1[Load climate.csv]  --> N2[Normalize APN (digits only)]

  N1 --> F1[Filter listings:
  - status in {for_sale,pending,sold}
  - required fields present
  - sqft > 0]
  F1 --> D1[Deduplicate by APN (keep lowest price)]
  D1 --> J1[Left-join climate on APN]
  J1 --> K1[Derived fields:
  - price_per_sqft = round(price/sqft)
  - full_address]
  K1 --> S1[Sort by price (asc)]
  S1 --> O1[Write JSON: data/listings_enriched.json]
```

## 3) Local Run Sequence

mermaid
```
sequenceDiagram
  participant Dev as Developer (VS Code)
  participant Py as Python (src/transform.py)
  participant FS as Filesystem
  participant DB as MySQL (Docker)

  Dev->>Py: python -m src.transform --listings ... --climate ...
  Py->>FS: Read CSVs (listings.csv, climate.csv)
  Py->>Py: Normalize → Filter → Dedup → Join → Derive → Sort
  Py->>FS: Write listings_enriched.json
  Dev->>Py: python -m scripts.load_to_mysql --json ...
  Py->>DB: REPLACE INTO listings_enriched (...)
  Dev->>DB: SELECT ... via scripts/query_mysql.py
```

## 4) Container/Infra (docker-compose)

mermaid
```
flowchart LR
  subgraph Host
    subgraph Repo
      D1[db/schema.sql, db/init.sql]
      J1[data/listings_enriched.json]
      S1[scripts/*.py]
    end
    subgraph Docker Desktop
      M[(mysql:8.0)]
    end
  end

  D1 -.mounted.-> M
  S1 -->|mysql-connector-python| M
  J1 --> S1
```

## 5) Data Model (ERD)
mermaid
```
erDiagram
  LISTINGS_ENRICHED {
    VARCHAR apn PK
    VARCHAR full_address
    INT     price
    INT     beds
    INT     baths
    INT     sqft
    INT     price_per_sqft
    VARCHAR status
    VARCHAR flood_zone
    DECIMAL avg_rain_inches
  }
```

## 6) Repository Layout
text

```
.
├─ data/
│  ├─ listings.csv
│  ├─ climate.csv
│  └─ listings_enriched.json   # build artifact
├─ db/
│  ├─ schema.sql               # table DDL
│  └─ init.sql                 # calls schema at first boot
├─ docs/
│  └─ architecture.md          # ← you are here
├─ scripts/
│  ├─ __init__.py
│  ├─ load_to_mysql.py         # loads JSON → MySQL
│  └─ query_mysql.py           # quick SQL runner
├─ src/
│  ├─ __init__.py
│  ├─ utils.py
│  └─ transform.py             # ETL (pandas)
├─ tests/
│  └─ test_transform.py
├─ .github/workflows/
│  └─ ci.yml                   # pytest + ETL sanity
├─ docker-compose.yml
├─ .env.example / .env
├─ .gitignore
└─ README.md
```

## 7) Local Commands (Runbook)

bash
```
# Transform → JSON
python -m src.transform --listings data/listings.csv --climate data/climate.csv --out data/listings_enriched.json

# Load JSON → MySQL
python -m scripts.load_to_mysql --json data/listings_enriched.json

# Ad-hoc queries
python -m scripts.query_mysql --sql "SELECT COUNT(*) AS total_rows FROM listings_enriched;"
```

## 8) CI Overview

GitHub Actions (.github/workflows/ci.yml) runs:

pip install -r requirements.txt

pytest

ETL sanity to ensure listings_enriched.json is produced

Badge for README (update with your repo):
![CI](https://github.com/kelvinAgramonte/real-estate-climate/actions/workflows/ci.yml/badge.svg)


---

## 2) Add and commit
yaml

```bat
git add docs\architecture.md
git commit -m "Docs: add architecture diagrams (Mermaid) and runbook"
```

