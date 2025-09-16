WITH last_order AS (
    SELECT customer_id, MAX(order_purchase_timestamp) AS last_order_date
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    CASE WHEN (CURRENT_DATE - lo.last_order_date::date) > 90 THEN 1 ELSE 0 END AS churned
FROM customers c
LEFT JOIN last_order lo ON c.customer_id = lo.customer_id;
