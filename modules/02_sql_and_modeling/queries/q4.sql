-- Q4. Which 3 customers have the highest revenue from completed orders?
--
-- Expected shape: 3 rows, 2 columns (customer_id, revenue), highest first.

SELECT customer_id AS customer, sum(quantity * unit_price) AS revenue
FROM orders_clean
WHERE status = 'completed'
GROUP BY customer
ORDER BY revenue DESC
LIMIT 3