# Module 01: Foundations

## What a data engineer does

Companies produce data in places built for *running* the business: the till
system, the app database, a payment provider. Those systems are bad places to
*answer questions* ("what sold best in March?"): the data is messy, scattered,
and querying it slows the business down.

A data engineer builds the plumbing in between: **pipelines** that move data
from where it is produced to where it can be analysed, and make it trustworthy
on the way. Analysts and data scientists are your customers.

## Three ideas for this module

### 1. Extract, transform, load

Almost every pipeline is some arrangement of three steps:

- **Extract**: get the data out of the source (a file, an API, a database).
- **Transform**: fix it and reshape it (clean, convert types, deduplicate, join).
- **Load**: write it where it will be queried (a warehouse).

Done in that order it is called **ETL**. Loading the raw data first and
transforming inside the warehouse with SQL is **ELT**, which is what most modern
teams do. You build ETL here and convert it to ELT in module 02, so you feel
the difference rather than memorise it.

### 2. Layers: never touch raw data

Data is kept in stages, and each stage is only ever written by code:


| Layer     | Holds                                   | Here                  |
| --------- | --------------------------------------- | --------------------- |
| Raw       | Exactly what the source sent, untouched | `data/raw/orders.csv` |
| Clean     | Typed, validated, deduplicated          | table `orders_clean`  |
| Analytics | Shaped for questions (module 02)        | later                 |


Raw stays untouched because your cleaning logic *will* have bugs. If you still
have the raw data, you fix the code and rerun. If you edited the raw file by
hand, the original is gone.

### 3. Idempotency

A pipeline is **idempotent** if running it twice gives the same result as
running it once. Pipelines get rerun constantly (a failure at 3am, a bug fix,
a retry), so a pipeline that doubles the data on a rerun is broken. This is
the single most important property you will design for in this course.

## Exercise

Setup, from the repo root:

```bash
source .venv/bin/activate
python scripts/generate_raw_data.py
```

**Step 1: look at the data before writing any code.** Always. Open
`data/raw/orders.csv` **and find at least four different things wrong with it.**

```bash
head -20 data/raw/orders.csv
```

**Step 2: write the transform.** Open `modules/01_foundations/pipeline.py` and
complete the three TODOs (`parse_date`, `clean_row`, `transform`). The
docstrings spell out the rules.

**Step 3: run and check.**

```bash
python modules/01_foundations/pipeline.py
python modules/01_foundations/check.py
```

**Step 4: query your warehouse.** This is what the work was for:

```bash
python -c "import duckdb; duckdb.connect('data/warehouse/shop.duckdb').sql('SELECT product, sum(total) AS revenue FROM orders_clean WHERE status = \'completed\' GROUP BY product ORDER BY revenue DESC').show()"
```

**Step 5: break idempotency on purpose.** Run the pipeline three times and
confirm the checker still passes. Then, in `load()`, change
`CREATE OR REPLACE TABLE` to `CREATE TABLE IF NOT EXISTS`, run it three more
times, and run the checker. Understand what happened, then put it back.

## Questions to answer in your own words

1. Why did the row count stay the same across reruns before your change, and
  not after?
2. `clean_row` silently drops bad rows. What could go wrong with that in a real
  company, and what would you rather do with those rows?
3. Two copies of an order had different formatting. Why would deduplicating
  *before* cleaning have failed?

When the checker passes, tell Claude "review my module 1" and give your answers.