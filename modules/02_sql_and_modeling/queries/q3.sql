-- Q3. What was the revenue of completed orders in each month?
--
-- Use month(order_date) to get the month as a number (1, 2, 3).
-- Expected shape: 3 rows, 2 columns (month number, revenue).

SELECT month(order_date), sum(unit_price * quantity) as revenue
FROM orders_clean
WHERE status = 'completed'
GROUP BY month(order_date)
ORDER BY revenue DESC