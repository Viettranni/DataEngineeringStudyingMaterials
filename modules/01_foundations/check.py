"""Check the result of the module 01 pipeline.

Run from the repo root, after running pipeline.py:
    python modules/01_foundations/check.py
"""
import sys
from pathlib import Path

import duckdb

WAREHOUSE = Path(__file__).resolve().parents[2] / "data" / "warehouse" / "shop.duckdb"

# Each check is a query that counts the rows breaking a rule; 0 means pass.
CHECKS = [
    ("has exactly 194 rows", "SELECT abs(count(*) - 194) FROM orders_clean"),
    ("order_id is never null", "SELECT count(*) FROM orders_clean WHERE order_id IS NULL"),
    ("order_id is unique", "SELECT count(*) - count(DISTINCT order_id) FROM orders_clean"),
    ("quantity is always positive", "SELECT count(*) FROM orders_clean WHERE quantity <= 0"),
    (
        "order_date falls in Jan-Mar 2026",
        "SELECT count(*) FROM orders_clean WHERE order_date NOT BETWEEN DATE '2026-01-01' AND DATE '2026-03-31'",
    ),
    (
        "status is one of completed / refunded / cancelled",
        "SELECT count(*) FROM orders_clean WHERE status NOT IN ('completed', 'refunded', 'cancelled')",
    ),
    (
        "customer_id has no stray whitespace",
        "SELECT count(*) FROM orders_clean WHERE customer_id <> trim(customer_id)",
    ),
    ("total = quantity * unit_price", "SELECT count(*) FROM orders_clean WHERE total <> quantity * unit_price"),
]


def main():
    if not WAREHOUSE.exists():
        sys.exit("No warehouse yet. Run modules/01_foundations/pipeline.py first.")
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    failed = 0
    for name, query in CHECKS:
        bad = con.execute(query).fetchone()[0]
        if bad:
            failed += 1
            print(f"FAIL  {name}  (off by {bad})")
        else:
            print(f"ok    {name}")
    con.close()
    if failed:
        sys.exit(f"\n{failed} of {len(CHECKS)} checks failed.")
    print("\nAll checks passed. Module 01 pipeline is correct.")


if __name__ == "__main__":
    main()
