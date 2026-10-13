-- fct_orders: one row per order, read from stg_orders.
--
-- Columns to produce: every column of stg_orders, plus
--   customer_order_number: 1 for a customer's first order, 2 for their second,
--                          and so on, counted by order_date and then order_id.

