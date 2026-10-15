-- Q2. How many orders are there for each status?
--
-- Expected shape: 3 rows, 2 columns (status, number of orders).

SELECT status, count(*) AS total
FROM orders_clean
GROUP BY status