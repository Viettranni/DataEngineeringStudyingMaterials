-- customer_summary: one row per customer in dim_customers, including the
-- customers who never ordered. Reads dim_customers and fct_orders.
--
-- Columns to produce:
--   customer_id
--   name
--   city
--   orders:   number of completed orders (0 if none)
--   revenue:  total of completed orders (0 if none)

