"""Module 01: your first pipeline (extract -> transform -> load).

Run from the repo root:
    python modules/01_foundations/pipeline.py

extract() and load() are written for you. Your job is the three TODOs in the
transform step.
"""
import csv
from datetime import datetime
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = ROOT / "data" / "raw" / "orders.csv"
WAREHOUSE = ROOT / "data" / "warehouse" / "shop.duckdb"

COLUMNS = ["order_id", "customer_id", "order_date", "product", "quantity", "unit_price", "status", "total"]


# --- Extract ---------------------------------------------------------------

def extract(path):
    """Read the raw CSV into a list of dicts. Every value is still a string."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# --- Transform -------------------------------------------------------------

def parse_date(text):
    """Return the date as an ISO string (YYYY-MM-DD).

    The raw file mixes two formats:
        "2026-03-14"  ->  "2026-03-14"
        "14/03/2026"  ->  "2026-03-14"

    Hint: datetime.strptime(text, fmt) raises ValueError if fmt does not match.
    """
    try:
        d = datetime.strptime(text, "%d/%m/%Y")
    except ValueError:
        d = datetime.strptime(text, "%Y-%m-%d")
    return d.date().isoformat()
    

def clean_row(row):
    """Turn one raw row into a clean, typed row, or None if it must be dropped.

    Rules:
      1. Strip surrounding whitespace from every value.
      2. Drop the row (return None) if order_id is empty.
      3. Drop the row if quantity is zero or negative.
      4. Lowercase status.
      5. Convert order_date with parse_date().
      6. Convert types: order_id and quantity -> int, unit_price -> float.
      7. Add total = quantity * unit_price, rounded to 2 decimals.

    The returned dict must have exactly the keys in COLUMNS.
    """
    cleaned = {}

    for key, value in row.items():
        cleaned[key] = value.strip()

    if cleaned["order_id"] == "":
        return None
    
    if int(cleaned["quantity"]) <= 0:
        return None
    
    cleaned["status"] = cleaned["status"].lower() 
    cleaned["order_date"] = parse_date(cleaned["order_date"])
    
    cleaned["order_id"] = int(cleaned["order_id"])
    cleaned["quantity"] = int(cleaned["quantity"])
    cleaned["unit_price"] = float(cleaned["unit_price"])

    cleaned["total"] = round((cleaned["quantity"] *  cleaned["unit_price"]), 2) 

    return cleaned




def transform(rows):
    """Clean every row and keep exactly one row per order_id.

    The source sometimes sends the same order twice, and the two copies may be
    formatted differently, so deduplicate on the cleaned order_id.
    """
    seen = set()
    result = []

    for row in rows:
        cleaned = clean_row(row)

        if cleaned == None:
            continue
        
        if cleaned["order_id"] in seen:
            continue

        seen.add(cleaned["order_id"])

        result.append(cleaned)
            

    return result

# --- Load ------------------------------------------------------------------

def load(rows, db_path):
    """Write the clean rows to the warehouse, replacing the previous contents."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute(
        """
        CREATE OR REPLACE TABLE orders_clean (
            order_id    INTEGER,
            customer_id VARCHAR,
            order_date  DATE,
            product     VARCHAR,
            quantity    INTEGER,
            unit_price  DECIMAL(10, 2),
            status      VARCHAR,
            total       DECIMAL(10, 2)
        )
        """
    )
    if rows:
        con.executemany(
            "INSERT INTO orders_clean VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [[row[column] for column in COLUMNS] for row in rows],
        )
    con.close()


def main():
    raw = extract(RAW_FILE)
    print(f"extract:   {len(raw)} raw rows")
    clean = transform(raw)
    print(f"transform: {len(clean)} clean rows ({len(raw) - len(clean)} dropped)")
    load(clean, WAREHOUSE)
    print(f"load:      orders_clean written to {WAREHOUSE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
