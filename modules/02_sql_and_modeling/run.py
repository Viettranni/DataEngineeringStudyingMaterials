"""Module 02: the ELT pipeline.

Run from the repo root:
    python modules/02_sql_and_modeling/run.py

This file is written for you. It does the E and the L (load the raw files into
the warehouse untouched), then runs your SQL models for the T. Each model is a
file in models/ holding one SELECT; the result is saved as a table named after
the file.
"""
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse" / "shop.duckdb"
MODELS_DIR = Path(__file__).resolve().parent / "models"

RAW_TABLES = {"raw_orders": "orders.csv", "raw_customers": "customers.csv"}

# Build order matters: a model can only read tables built before it.
MODELS = ["stg_orders", "dim_customers", "fct_orders", "customer_summary"]


def read_sql(path):
    """Return the SQL in a file without comment lines, or "" if there is none."""
    lines = [line for line in path.read_text().splitlines() if not line.strip().startswith("--")]
    return "\n".join(lines).strip().rstrip(";").strip()


def load_raw(con):
    """Copy each raw file into a table, every column as text, nothing changed."""
    for table, filename in RAW_TABLES.items():
        path = RAW_DIR / filename
        if not path.exists():
            sys.exit(f"{path.relative_to(ROOT)} is missing. Run: python scripts/generate_raw_data.py")
        con.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv('{path}', header = true, all_varchar = true)"
        )
        rows = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"load:   {table} ({rows} rows)")


def build_models(con):
    for name in MODELS:
        sql = read_sql(MODELS_DIR / f"{name}.sql")
        if not sql:
            print(f"todo:   {name} (models/{name}.sql has no query yet)")
            return
        try:
            con.execute(f"CREATE OR REPLACE TABLE {name} AS {sql}")
        except duckdb.Error as error:
            sys.exit(f"error:  {name}\n\n{error}")
        rows = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        print(f"build:  {name} ({rows} rows)")


def main():
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    load_raw(con)
    build_models(con)
    con.close()


if __name__ == "__main__":
    main()
