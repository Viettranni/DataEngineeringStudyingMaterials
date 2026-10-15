-- Q1. How many orders in orders_clean were refunded?
--
-- Expected shape: 1 row, 1 column (the count).

SELECT count(*)
FROM orders_clean
WHERE status = 'refunded'