"""Check the module 02 queries and models.

Run from the repo root, after running run.py:
    python modules/02_sql_and_modeling/check.py
"""
import sys
from decimal import Decimal
from pathlib import Path

import duckdb

from run import WAREHOUSE, read_sql

QUERIES_DIR = Path(__file__).resolve().parent / "queries"

ORDER_COLUMNS = "order_id, customer_id, order_date, product, quantity, unit_price, status, total"
COMPLETED = "SELECT {} FROM stg_orders WHERE status = 'completed'"

# Part 1: the rows each query must return (row order is not checked).
QUERIES = {
    "q1": [(41,)],
    "q2": [("cancelled", 33), ("completed", 120), ("refunded", 41)],
    "q3": [(1, 640.50), (2, 652.40), (3, 757.40)],
    "q4": [("C018", 133.50), ("C020", 114.60), ("C040", 206.85)],
}

# Parts 2 and 3: each check is a query that returns 0 when the rule holds.
MODELS = {
    "stg_orders": [
        ("has exactly 194 rows", "SELECT abs(count(*) - 194) FROM stg_orders"),
        ("order_id is unique and never null", "SELECT count(*) - count(DISTINCT order_id) FROM stg_orders"),
        ("order_id and quantity are integers", "SELECT count(*) FROM stg_orders WHERE typeof(order_id) NOT IN ('INTEGER', 'BIGINT') OR typeof(quantity) NOT IN ('INTEGER', 'BIGINT')"),
        ("order_date is a DATE", "SELECT count(*) FROM stg_orders WHERE typeof(order_date) <> 'DATE' OR order_date IS NULL"),
        ("unit_price is a DECIMAL", "SELECT count(*) FROM stg_orders WHERE typeof(unit_price) NOT LIKE 'DECIMAL%'"),
        ("quantity is always positive", "SELECT count(*) FROM stg_orders WHERE quantity <= 0"),
        ("status is lowercase with no spaces", "SELECT count(*) FROM stg_orders WHERE status NOT IN ('completed', 'refunded', 'cancelled')"),
        ("customer_id has no stray whitespace", "SELECT count(*) FROM stg_orders WHERE customer_id <> trim(customer_id)"),
        ("total = quantity * unit_price", "SELECT count(*) FROM stg_orders WHERE total <> quantity * unit_price"),
        (
            "matches orders_clean, the table your Python pipeline built",
            f"SELECT count(*) FROM (SELECT {ORDER_COLUMNS} FROM stg_orders EXCEPT SELECT {ORDER_COLUMNS} FROM orders_clean)",
        ),
    ],
    "dim_customers": [
        ("has exactly 45 rows", "SELECT abs(count(*) - 45) FROM dim_customers"),
        ("customer_id is unique and never null", "SELECT count(*) - count(DISTINCT customer_id) FROM dim_customers"),
        ("name and city are filled in", "SELECT count(*) FROM dim_customers WHERE name IS NULL OR city IS NULL"),
        ("signup_date is a DATE", "SELECT count(*) FROM dim_customers WHERE typeof(signup_date) <> 'DATE' OR signup_date IS NULL"),
    ],
    "fct_orders": [
        ("has the same orders as stg_orders", f"SELECT count(*) FROM (SELECT {ORDER_COLUMNS} FROM stg_orders EXCEPT SELECT {ORDER_COLUMNS} FROM fct_orders)"),
        ("has one row per order", "SELECT abs(count(*) - 194) + count(*) - count(DISTINCT order_id) FROM fct_orders"),
        (
            "customer_order_number runs 1, 2, 3... for each customer",
            "SELECT count(*) FROM (SELECT customer_id FROM fct_orders GROUP BY customer_id"
            " HAVING min(customer_order_number) <> 1 OR max(customer_order_number) <> count(*)"
            " OR count(DISTINCT customer_order_number) <> count(*))",
        ),
        (
            "customer_order_number follows order_date, then order_id",
            "SELECT count(*) FROM fct_orders a JOIN fct_orders b ON a.customer_id = b.customer_id"
            " WHERE (a.order_date < b.order_date OR (a.order_date = b.order_date AND a.order_id < b.order_id))"
            " AND a.customer_order_number > b.customer_order_number",
        ),
    ],
    "customer_summary": [
        ("has one row per customer (45), including those with no orders", "SELECT abs(count(*) - 45) + count(*) - count(DISTINCT customer_id) FROM customer_summary"),
        ("orders and revenue are never null", "SELECT count(*) FROM customer_summary WHERE orders IS NULL OR revenue IS NULL"),
        (
            "customers with no completed orders show 0 orders",
            "SELECT count(*) FROM customer_summary WHERE orders <> 0"
            f" AND customer_id NOT IN ({COMPLETED.format('customer_id')})",
        ),
        ("orders adds up to the number of completed orders", f"SELECT abs((SELECT sum(orders) FROM customer_summary) - ({COMPLETED.format('count(*)')}))"),
        ("revenue adds up to the revenue of completed orders", f"SELECT round(abs((SELECT sum(revenue) FROM customer_summary) - ({COMPLETED.format('sum(total)')})), 2)"),
    ],
}


def normalise(rows):
    """Make results comparable: numbers as rounded floats, rows in a fixed order."""
    cleaned = []
    for row in rows:
        cleaned.append(tuple(round(float(v), 2) if isinstance(v, (int, float, Decimal)) else v for v in row))
    return sorted(cleaned, key=repr)


def check_query(con, name, expected):
    sql = read_sql(QUERIES_DIR / f"{name}.sql")
    if not sql:
        return "todo", "no query yet"
    try:
        got = con.execute(sql).fetchall()
    except duckdb.Error as error:
        return "FAIL", str(error).splitlines()[0]
    if normalise(got) == normalise(expected):
        return "ok", ""
    shape = f"{len(got)} rows x {len(got[0]) if got else 0} columns"
    return "FAIL", f"got {shape}: {normalise(got)[:4]}, expected {normalise(expected)}"


def check_rule(con, sql):
    try:
        bad = con.execute(sql).fetchone()[0]
    except duckdb.Error as error:
        return "FAIL", str(error).splitlines()[0]
    if bad == 0:
        return "ok", ""
    return "FAIL", "the result is empty or null" if bad is None else f"off by {bad}"


def report(status, name, detail):
    print(f"  {status:<5} {name}" + (f"  ({detail})" if detail else ""))
    return status


def main():
    if not WAREHOUSE.exists():
        sys.exit("No warehouse yet. Run modules/01_foundations/pipeline.py first.")
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    statuses = []

    print("Part 1: queries")
    for name, expected in QUERIES.items():
        status, detail = check_query(con, name, expected)
        statuses.append(report(status, name, detail))

    for number, (table, rules) in enumerate(MODELS.items()):
        print(f"\nPart {2 if number == 0 else 3}: {table}")
        if table not in tables:
            statuses.append(report("todo", table, "not built yet: write the model, then run run.py"))
            continue
        for name, sql in rules:
            status, detail = check_rule(con, sql)
            statuses.append(report(status, name, detail))
    con.close()

    todo, failed = statuses.count("todo"), statuses.count("FAIL")
    if todo or failed:
        sys.exit(f"\n{statuses.count('ok')} ok, {failed} failed, {todo} still to do.")
    print("\nAll checks passed. Module 02 is complete.")


if __name__ == "__main__":
    main()
