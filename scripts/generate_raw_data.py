"""Generate the messy raw data used throughout the course.

The output is deterministic (fixed seed), so the file is identical every time
and the module checkers know what a correct result looks like.

Run from the repo root:
    python scripts/generate_raw_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

PRODUCTS = {
    "espresso": 2.80,
    "latte": 4.20,
    "cappuccino": 4.00,
    "cold brew": 4.50,
    "croissant": 3.25,
    "beans 250g": 11.90,
}
STATUSES = ["completed", "completed", "completed", "refunded", "cancelled"]
COLUMNS = ["order_id", "customer_id", "order_date", "product", "quantity", "unit_price", "status"]

FIRST_NAMES = ["Aino", "Eero", "Helmi", "Onni", "Sofia", "Leo", "Venla", "Elias", "Ella", "Noel"]
LAST_NAMES = ["Virtanen", "Korhonen", "Nieminen", "Laine", "Koskinen", "Salo", "Lehtonen", "Heikkinen"]
CITIES = ["Helsinki", "Espoo", "Tampere", "Turku", "Oulu"]


def make_order(rng, order_id):
    product = rng.choice(list(PRODUCTS))
    day = date(2026, 1, 1) + timedelta(days=rng.randrange(90))
    return {
        "order_id": str(order_id),
        "customer_id": f"C{rng.randrange(1, 41):03d}",
        "order_date": day.isoformat(),
        "product": product,
        "quantity": str(rng.randint(1, 5)),
        "unit_price": f"{PRODUCTS[product]:.2f}",
        "status": rng.choice(STATUSES),
    }


def write_csv(filename, columns, rows):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def write_customers():
    rng = random.Random(7)  # its own seed, so adding this never changes orders.csv
    rows = []
    for number in range(1, 46):  # C041-C045 never order anything
        signup = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        rows.append(
            {
                "customer_id": f"C{number:03d}",
                "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "city": rng.choice(CITIES),
                "signup_date": signup.isoformat(),
            }
        )
    write_csv("customers.csv", ["customer_id", "name", "city", "signup_date"], rows)


def write_orders():
    rng = random.Random(42)
    orders = [make_order(rng, order_id) for order_id in range(1001, 1201)]

    # Problems a real source system would hand you:
    for row in rng.sample(orders, 6):  # impossible quantities
        row["quantity"] = rng.choice(["0", "-1"])
    valid = [row for row in orders if int(row["quantity"]) > 0]
    duplicates = [dict(row) for row in rng.sample(valid, 8)]  # same order sent twice
    orphans = [make_order(rng, "") for _ in range(5)]  # no order id at all

    rows = orders + duplicates + orphans
    for row in rows:  # inconsistent formatting
        if rng.random() < 0.25:
            row["order_date"] = date.fromisoformat(row["order_date"]).strftime("%d/%m/%Y")
        if rng.random() < 0.30:
            status = row["status"]
            row["status"] = rng.choice([status.upper(), status.title(), f" {status} "])
        if rng.random() < 0.15:
            row["customer_id"] = f" {row['customer_id']} "
    rng.shuffle(rows)
    write_csv("orders.csv", COLUMNS, rows)


if __name__ == "__main__":
    write_orders()
    write_customers()
