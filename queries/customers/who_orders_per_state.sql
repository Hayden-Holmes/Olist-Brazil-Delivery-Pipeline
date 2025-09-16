SELECT c.customer_state AS state,
        COUNT(DISTINCT o.customer_id) AS total_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_customers DESC;
 