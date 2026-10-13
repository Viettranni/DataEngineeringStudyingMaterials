"""Run SQL against the warehouse and print the result.

Run from the repo root, with either a query or a .sql file:
    python scripts/sql.py "SELECT * FROM orders_clean LIMIT 5"
    python scripts/sql.py modules/02_sql_and_modeling/queries/q1.sql
"""
import sys
from pathlib import Path

import duckdb

WAREHOUSE = Path(__file__).resolve().parents[1] / "data" / "warehouse" / "shop.duckdb"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    query = sys.argv[1]
    if query.endswith(".sql"):
        query = Path(query).read_text()
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    try:
        result = con.sql(query)
    except duckdb.Error as error:
        sys.exit(str(error))
    if result is None:
        print("Nothing to show (the file has no query in it yet).")
    else:
        result.show(max_rows=60)


if __name__ == "__main__":
    main()
