# Module 02: SQL and data modeling

In module 01 you cleaned the data in Python and then loaded it: **ETL**. Here
you flip the order. The raw data is loaded into the warehouse untouched, and
the cleaning is written in SQL, inside the warehouse: **ELT**. Then you shape
the clean data into tables designed for answering questions.

The module has three parts. Do them in order, and run the checker as often as
you like; it shows `todo` for what you have not reached yet.

```bash
source .venv/bin/activate
python modules/02_sql_and_modeling/check.py
```

## Running SQL

`scripts/sql.py` runs a query, or a `.sql` file, and prints the result:

```bash
python scripts/sql.py "SELECT * FROM orders_clean LIMIT 5"
python scripts/sql.py modules/02_sql_and_modeling/queries/q1.sql
```

Use it constantly. Run a query, look at the output, change one thing, run it
again. That loop is how SQL is learned.

---

## Part 1: asking questions with SQL

A table is rows and columns. A query describes the rows and columns you want
back, and the database works out how to get them.

```sql
SELECT product, quantity, total     -- which columns
FROM orders_clean                   -- from which table
WHERE status = 'completed'          -- keep only rows where this is true
ORDER BY total DESC                 -- sort, biggest first
LIMIT 5                             -- stop after 5 rows
```

Text values go in single quotes (`'completed'`). `SELECT *` means every column.

**Aggregates** squash many rows into one value: `count(*)`, `sum(total)`,
`avg(total)`, `min(...)`, `max(...)`.

```sql
SELECT count(*), sum(total)
FROM orders_clean
WHERE status = 'completed'
```

**GROUP BY** gives one result row per group instead of one for the whole table:

```sql
SELECT product, sum(total) AS revenue    -- AS names the new column
FROM orders_clean
WHERE status = 'completed'
GROUP BY product
ORDER BY revenue DESC
```

Read it as: split the rows into piles by product, then add up each pile. Every
column in the SELECT must either be in the GROUP BY or be inside an aggregate.

### Exercise

Answer the four questions in `queries/q1.sql` to `queries/q4.sql`. Each file
states its question at the top; write one query below it.

---

## Part 2: ELT

Run the pipeline once now:

```bash
python modules/02_sql_and_modeling/run.py
python scripts/sql.py "SELECT * FROM raw_orders LIMIT 10"
```

`run.py` loaded `orders.csv` into a table called `raw_orders` without changing
anything: the stray spaces, mixed date formats and duplicates are all in there,
and every column is text. That is the raw layer living inside the warehouse.

Your job is the **staging** model `models/stg_orders.sql`: one SELECT that
reads `raw_orders` and returns the clean rows. `run.py` saves the result as the
table `stg_orders` (the file name), replacing it on every run, so the pipeline
is idempotent without you doing anything.

Everything you did in Python has a SQL equivalent:

| In Python (module 01)            | In SQL                                                        |
|----------------------------------|---------------------------------------------------------------|
| `value.strip()`                  | `trim(customer_id)`                                           |
| `value.lower()`                  | `lower(status)`                                               |
| `int(value)`                     | `CAST(quantity AS INTEGER)`                                   |
| `float(value)`                   | `CAST(unit_price AS DECIMAL(10, 2))`                          |
| `parse_date` with try / except   | `CAST(try_strptime(order_date, ['%Y-%m-%d', '%d/%m/%Y']) AS DATE)` |
| `if ...: return None`            | `WHERE` keeps only the rows you want                          |
| the `seen` set                   | `SELECT DISTINCT` removes rows that are identical             |
| `cleaned["total"] = ...`         | `quantity * unit_price AS total`                              |

Three things that differ from Python:

- You name each output column with `AS`: `trim(customer_id) AS customer_id`.
- An empty CSV field arrives as `NULL`, SQL's "no value". Test for it with
  `order_id IS NULL` or `IS NOT NULL`, never with `=`.
- A column you just named with `AS` cannot be reused in the same SELECT's
  `WHERE`, so repeat the expression: `WHERE CAST(quantity AS INTEGER) > 0`.

`DISTINCT` only removes the duplicates here because the two copies of an order
are identical *after* cleaning. It compares the cleaned output, which is why it
works; the same reasoning as module 01's question 3.

### Exercise

Write `models/stg_orders.sql`, then:

```bash
python modules/02_sql_and_modeling/run.py
python modules/02_sql_and_modeling/check.py
```

The last check compares `stg_orders` with `orders_clean`, the table your Python
pipeline built. Two different programs, same result.

---

## Part 3: modeling

Clean data is not yet convenient data. Analysts ask things like "revenue by
city", and city is not in the orders at all: it is in `customers.csv`. Data
modeling is deciding which tables to build so questions like that are easy.

The standard design is the **star schema**, with two kinds of table:

- A **fact** table records events: things that happened, one row each. Here,
  `fct_orders`, one row per order.
- A **dimension** table describes the things involved in those events. Here,
  `dim_customers`, one row per customer.

For every table, be able to say what one row is. That is called its **grain**,
and getting it wrong is the most common modeling bug.

### Joins

A join combines two tables by matching a column they share:

```sql
SELECT o.order_id, o.total, c.city
FROM fct_orders AS o
JOIN dim_customers AS c ON c.customer_id = o.customer_id
```

`o` and `c` are short names for the tables. There are two kinds you need:

- `JOIN` (inner) keeps only the rows that have a match on both sides.
- `LEFT JOIN` keeps every row of the left (first) table. Where there is no
  match, the right table's columns come back as `NULL`.

Five customers have never ordered. An inner join drops them; a
`dim_customers LEFT JOIN fct_orders` keeps them, with NULLs for the order
columns. Two consequences catch everybody once:

1. **A `WHERE` on the right table undoes the LEFT JOIN.** `WHERE o.status =
   'completed'` throws away the NULL rows, and with them the customers who have
   no orders. Put the condition in the join instead:
   `LEFT JOIN fct_orders AS o ON o.customer_id = c.customer_id AND o.status = 'completed'`.
2. **`count(*)` counts the NULL row too**, so a customer with no orders shows 1.
   `count(o.order_id)` counts only real orders, because it skips NULLs. For the
   same reason `sum(o.total)` is NULL for them; `coalesce(sum(o.total), 0)`
   turns a NULL into 0.

### Window functions

GROUP BY collapses rows. A **window function** calculates across a group of
rows but keeps every row. This numbers each customer's orders from oldest to
newest:

```sql
row_number() OVER (PARTITION BY customer_id ORDER BY order_date, order_id)
```

`PARTITION BY` is the group, `ORDER BY` is the order inside it. Use it like any
other column, with `AS` to name it.

### Exercise

Write the three models, one at a time, running `run.py` and `check.py` after
each. The columns each must produce are listed at the top of its file.

1. `models/dim_customers.sql`: a cast and nothing else. A warm-up.
2. `models/fct_orders.sql`: `stg_orders` plus one window function.
3. `models/customer_summary.sql`: a LEFT JOIN with GROUP BY. This is the hard
   one; both traps above apply.

Then use what you built:

```bash
python scripts/sql.py "SELECT city, sum(revenue) AS revenue FROM customer_summary GROUP BY city ORDER BY revenue DESC"
```

## Questions to answer in your own words

1. In ELT the raw data sits in the warehouse as `raw_orders`. What can you do
   now that you could not do when the cleaning happened in Python before the
   load?
2. What is the grain of `fct_orders`, of `dim_customers`, and of
   `customer_summary`?
3. `fct_orders` keeps `unit_price` on every order instead of looking it up from
   a product table. Why might that be the right choice when prices change?

When the checker passes, tell Claude "review my module 2" and give your answers.
