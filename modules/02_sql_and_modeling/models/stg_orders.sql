-- stg_orders: the cleaned orders, one row per order. Same rules as module 01,
-- written as one SELECT that reads from raw_orders.
--
-- Columns to produce (name: type):
--   order_id:    INTEGER
--   customer_id: text, no surrounding spaces
--   order_date:  DATE
--   product:     text
--   quantity:    INTEGER
--   unit_price:  DECIMAL(10, 2)
--   status:      text, lowercase, no surrounding spaces
--   total:       quantity * unit_price
--
-- Rows to drop: no order_id, quantity of zero or less, duplicates.

SELECT DISTINCT
CAST(order_id AS INTEGER) AS order_id, 
trim(customer_id) AS customer_id, 
CAST(try_strptime(order_date, ['%Y-%m-%d', '%d/%m/%Y']) AS DATE) AS order_date, 
product, 
CAST(quantity AS INTEGER) AS quantity,
CAST(unit_price AS DECIMAL(10, 2)) AS unit_price,
trim(lower(status)) AS status, 
CAST(quantity AS INTEGER) * CAST(unit_price AS DECIMAL(10, 2)) AS total
FROM raw_orders
WHERE order_id IS NOT NULL
AND CAST(quantity AS INTEGER) > 0 